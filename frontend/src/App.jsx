import { useState, useEffect, createContext, useContext } from 'react';
import { authAPI, searchAPI, chatAPI, circularsAPI } from './services/api';

// Auth Context
const AuthContext = createContext(null);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      setUser({ token });
    } else {
      localStorage.removeItem('token');
      setUser(null);
    }
  }, [token]);

  const login = async (email, password) => {
    const response = await authAPI.login(email, password);
    setToken(response.data.access_token);
    return response.data;
  };

  const register = async (email, password) => {
    const response = await authAPI.register(email, password);
    setToken(response.data.access_token);
    return response.data;
  };

  const logout = () => {
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// Login Component
const LoginPage = ({ onSwitch }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">RegRadar</h1>
        <p className="text-gray-600 mb-6">AI-Powered Regulatory Intelligence</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
              minLength={8}
            />
          </div>

          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-blue-300 transition"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <button onClick={onSwitch} className="text-blue-600 hover:underline">Register</button>
        </p>
      </div>
    </div>
  );
};

// Register Component
const RegisterPage = ({ onSwitch }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(email, password);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Account</h1>
        <p className="text-gray-600 mb-6">Get started with RegRadar</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
              minLength={8}
            />
            <p className="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
          </div>

          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-blue-300 transition"
          >
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          Already have an account?{' '}
          <button onClick={onSwitch} className="text-blue-600 hover:underline">Login</button>
        </p>
      </div>
    </div>
  );
};

// Main Dashboard
const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('search');
  const { logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">RegRadar</h1>
            <p className="text-sm text-gray-600">AI Regulatory Intelligence</p>
          </div>
          <button
            onClick={logout}
            className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            {['search', 'chat', 'circulars'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize transition ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'search' && <SearchTab />}
        {activeTab === 'chat' && <ChatTab />}
        {activeTab === 'circulars' && <CircularsTab />}
      </main>
    </div>
  );
};

// Search Tab
const SearchTab = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    try {
      const response = await searchAPI.search(query, 5);
      setResults(response.data.results);
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Semantic Search</h2>
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search regulations... (e.g., 'capital adequacy requirements')"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300 transition"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
        {error && <div className="mt-4 bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>}
      </div>

      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {results.length} Results for "{query}"
          </h3>
          {results.map((result, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-gray-900">{result.circular_title}</h4>
                <span className="text-sm font-medium text-blue-600">
                  {(result.relevance_score * 100).toFixed(0)}% match
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                <span className="uppercase font-medium">{result.source}</span>
                <span>Page {result.page_number}</span>
                {result.date && <span>{result.date}</span>}
              </div>
              <p className="text-gray-700 text-sm">{result.text_preview}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Chat Tab
const ChatTab = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError('');
    try {
      const response = await chatAPI.ask(question, 5);
      setAnswer(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get answer');
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Ask a Question</h2>
        <form onSubmit={handleAsk} className="space-y-4">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask anything about RBI or SEBI regulations..."
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300 transition"
          >
            {loading ? 'Getting answer...' : 'Ask'}
          </button>
        </form>
        {error && <div className="mt-4 bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>}
      </div>

      {answer && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Answer</h3>
            <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
              {answer.answer}
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Sources</h3>
            <div className="space-y-2">
              {answer.citations.map((citation, idx) => (
                <div key={idx} className="flex items-center gap-4 text-sm text-gray-600 p-3 bg-gray-50 rounded">
                  <span className="font-medium">{idx + 1}.</span>
                  <span className="flex-1">{citation.circular_title}</span>
                  <span className="uppercase font-medium">{citation.source}</span>
                  <span>Page {citation.page_number}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Circulars Tab
const CircularsTab = () => {
  const [circulars, setCirculars] = useState([]);
  const [loading, setLoading] = useState(false);
  const [source, setSource] = useState('');

  useEffect(() => {
    loadCirculars();
  }, [source]);

  const loadCirculars = async () => {
    setLoading(true);
    try {
      const response = await circularsAPI.list(0, 20, source || null);
      setCirculars(response.data);
    } catch (err) {
      console.error('Failed to load circulars:', err);
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Indexed Circulars</h2>
          <select
            value={source}
            onChange={(e) => setSource(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Sources</option>
            <option value="rbi">RBI</option>
            <option value="sebi">SEBI</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading circulars...</div>
      ) : circulars.length > 0 ? (
        <div className="space-y-4">
          {circulars.map((circular) => (
            <div key={circular.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-900 flex-1">{circular.title}</h3>
                <span className="text-xs uppercase font-medium text-blue-600 px-2 py-1 bg-blue-50 rounded">
                  {circular.source}
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                {circular.date && <span>{circular.date}</span>}
                <span>{new Date(circular.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">No circulars found</div>
      )}
    </div>
  );
};

// Main App
function App() {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <AuthProvider>
      <AuthContext.Consumer>
        {({ user }) => (
          user ? (
            <Dashboard />
          ) : isLogin ? (
            <LoginPage onSwitch={() => setIsLogin(false)} />
          ) : (
            <RegisterPage onSwitch={() => setIsLogin(true)} />
          )
        )}
      </AuthContext.Consumer>
    </AuthProvider>
  );
}

export default App;
