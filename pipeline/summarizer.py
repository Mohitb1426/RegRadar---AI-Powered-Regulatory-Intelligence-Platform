"""
AI summarization using AWS Bedrock Claude Sonnet 4
Generates concise summaries of regulatory circulars
"""

import os
import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_BEDROCK_MODEL = os.getenv("AWS_BEDROCK_MODEL", "anthropic.claude-sonnet-4-20250514-v1:0")


class BedrockSummarizer:
    """AWS Bedrock Claude summarization service"""

    def __init__(self):
        if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]):
            raise ValueError("AWS credentials not configured")

        # Build client args
        client_args = {
            "service_name": "bedrock-runtime",
            "aws_access_key_id": AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
            "region_name": AWS_REGION
        }

        # Add session token if provided (for temporary credentials)
        if AWS_SESSION_TOKEN:
            client_args["aws_session_token"] = AWS_SESSION_TOKEN

        self.client = boto3.client(**client_args)
        self.model_id = AWS_BEDROCK_MODEL

    def generate(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """
        Generate text using Claude via AWS Bedrock

        Args:
            prompt: The prompt to send to Claude
            max_tokens: Maximum tokens in response

        Returns:
            Generated text or None if error
        """
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3
            })

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']

        except ClientError as e:
            print(f"  [ERROR] AWS Bedrock error: {e}")
            return None
        except Exception as e:
            print(f"  [ERROR] Summarization error: {e}")
            return None

    def summarize_circular(self, circular_text: str, title: str, source: str) -> Optional[str]:
        """
        Generate summary of regulatory circular

        Args:
            circular_text: Full text of the circular
            title: Circular title
            source: 'rbi' or 'sebi'

        Returns:
            Summary string or None if error
        """
        # Truncate text if too long (Bedrock has token limits)
        max_chars = 15000
        if len(circular_text) > max_chars:
            circular_text = circular_text[:max_chars] + "\n\n[Text truncated...]"

        prompt = f"""You are a regulatory compliance expert. Summarize the following {source.upper()} circular in a clear, structured format.

Title: {title}

Circular Text:
{circular_text}

Provide a comprehensive summary that covers:
1. **Key Regulations**: Main regulatory changes or guidelines
2. **Who It Affects**: Target entities (banks, NBFCs, market participants, etc.)
3. **Effective Date**: When the regulation comes into effect
4. **Action Required**: What entities need to do to comply
5. **Important Deadlines**: Any critical dates to note

Keep the summary concise but comprehensive (300-500 words). Use bullet points where appropriate for clarity.

Summary:"""

        return self.generate(prompt, max_tokens=1000)

    def answer_question(self, question: str, context_chunks: list) -> Optional[str]:
        """
        Answer question based on retrieved circular chunks (RAG)

        Args:
            question: User's question
            context_chunks: List of relevant text chunks from Pinecone

        Returns:
            Answer string or None if error
        """
        # Combine context chunks
        context_text = "\n\n".join([
            f"[{chunk['metadata']['source'].upper()} - {chunk['metadata']['circular_title'][:100]} - Page {chunk['metadata']['page_number']}]\n{chunk['metadata']['text']}"
            for chunk in context_chunks
        ])

        prompt = f"""You are a regulatory compliance expert. Answer the user's question based on the following circular excerpts from RBI and SEBI.

Context from Circulars:
{context_text}

User Question: {question}

Instructions:
1. Answer the question directly and concisely
2. Cite specific circulars and page numbers when referencing information
3. If the context doesn't contain enough information, say so
4. Format your answer clearly with bullet points where appropriate

Answer:"""

        return self.generate(prompt, max_tokens=800)


def summarize_circulars(circulars_list: list) -> list:
    """
    Generate summaries for all circulars

    Returns:
        List of circulars with summaries added
    """
    print("\n" + "=" * 60)
    print("Starting AI summarization...")
    print("=" * 60)

    summarizer = BedrockSummarizer()
    summarized_circulars = []

    for circular in circulars_list:
        if 'parsed_data' not in circular:
            print(f"  [SKIP] Skipping (not parsed): {circular['title'][:60]}...")
            continue

        print(f"\n[AI] Summarizing: {circular['title'][:60]}...")

        full_text = circular['parsed_data']['full_text']
        title = circular['title']
        source = circular['source']

        summary = summarizer.summarize_circular(full_text, title, source)

        if summary:
            circular['summary'] = summary
            summarized_circulars.append(circular)
            print(f"  [OK] Summary generated ({len(summary)} chars)")

            # Show preview of summary
            preview = summary[:200].replace('\n', ' ')
            print(f"  Preview: {preview}...")
        else:
            print(f"  [ERROR] Summarization failed")

    print("\n" + "=" * 60)
    print(f"Successfully summarized: {len(summarized_circulars)}/{len(circulars_list)}")
    print("=" * 60)

    return summarized_circulars


if __name__ == "__main__":
    # Test Bedrock connection
    print("Testing AWS Bedrock Claude Sonnet 4...")

    summarizer = BedrockSummarizer()

    test_text = """
    Reserve Bank of India
    RBI/2024/KYC/001

    Master Direction on Know Your Customer (KYC) Norms

    All Scheduled Commercial Banks are advised to implement enhanced KYC procedures
    for high-risk customers. The following guidelines must be followed:

    1. Customer Due Diligence: Enhanced CDD for politically exposed persons
    2. Document Verification: Mandatory Aadhaar-based verification
    3. Monitoring: Continuous transaction monitoring for suspicious activities
    4. Reporting: Monthly reports to RBI by 15th of following month

    Effective Date: April 1, 2024
    """

    summary = summarizer.summarize_circular(
        circular_text=test_text,
        title="Master Direction on KYC Norms",
        source="rbi"
    )

    if summary:
        print("\n[OK] Test successful!")
        print("\nGenerated Summary:")
        print("-" * 60)
        print(summary)
        print("-" * 60)
    else:
        print("\n[ERROR] Test failed")
