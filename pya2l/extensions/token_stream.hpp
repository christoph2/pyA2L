
#if !defined(__TOKEN_STREAM_HPP)
    #define __TOKEN_STREAM_HPP

    // #define __STDC_WANT_LIB_EXT1__ (1)
    #include <sys/types.h>

    #include <algorithm>
    #include <cstdio>
    #include <deque>
    #include <ranges>

    #include "exceptions.hpp"
    #include "tempfile.hpp"
    #include "tokenizer.hpp"
    #if defined(_WIN32)
        #pragma warning(disable: 4251 4273)
    #endif

template<typename Ty_>
class FixedSizeStack {
   public:

    explicit FixedSizeStack(std::size_t size) : m_size(size) {
    }

    FixedSizeStack(const FixedSizeStack &)            = delete;
    FixedSizeStack &operator=(const FixedSizeStack &) = delete;
    FixedSizeStack(FixedSizeStack &&)                 = delete;
    FixedSizeStack &operator=(FixedSizeStack &&)      = delete;

    //~FixedSizeStack() = default;

    void push(const Ty_ &value) noexcept {
        m_stack.push_front(value);
        if (m_stack.size() > m_size) {
            m_stack.pop_back();
        }
    }

    const Ty_ &operator[](std::size_t index) {
        return m_stack[index];
    }

   private:

    std::deque<Ty_> m_stack{};
    std::size_t     m_size;
};

class TokenWriter {
   public:

    const std::size_t HEADER_SIZE = sizeof(std::size_t) * 6;

    TokenWriter() = delete;

    explicit TokenWriter(TempFile &outf) : m_outf(outf.handle()) {
    }

    void operator<<(const Token &token) const {
        if ((token.m_token_class == TokenClass::REGULAR) || (token.m_token_class == TokenClass::STRING)) {
            write_int(std::size(token.m_payload));
            write_int(token.m_token_type);
            write_int(token.m_line_numbers.start_line);
            write_int(token.m_line_numbers.start_col);
            write_int(token.m_line_numbers.end_line);
            write_int(token.m_line_numbers.end_col);

            write_string(token.m_payload);
        }
    }

    void write_int(std::size_t value) const {
        // const std::size_t before = m_outf.tellp();
        m_outf.write(std::bit_cast<const char *>(&value), sizeof(std::size_t));
    #if 0
// Testing code.
        const std::size_t after   = m_outf.tellp();
        const std::size_t correct = before + 8;
        assert(correct == after);
    #endif
    }

    void write_string(std::string_view text) const {
        m_outf.write(text.data(), std::size(text));
    }

   private:

    std::ofstream &m_outf;
};

class ANTLRToken /*: public antlr4::Token*/ {
   public:

    using token_t = unsigned long long;
    static std::string encoding;

    static constexpr size_t INVALID_TYPE           = 0;
    static constexpr size_t EPSILON                = std::numeric_limits<size_t>::max() - 1;
    static constexpr size_t MIN_USER_TOKEN_TYPE    = 1;
    static constexpr size_t _EOF                   = std::numeric_limits<size_t>::max();
    static constexpr size_t DEFAULT_CHANNEL        = 0;
    static constexpr size_t HIDDEN_CHANNEL         = 1;
    static constexpr size_t MIN_USER_CHANNEL_VALUE = 2;

    ANTLRToken()                   = default;
    ANTLRToken(const ANTLRToken &) = default;

    //~ANTLRToken() = default;

    ANTLRToken(ANTLRToken &&other) noexcept {
        // std::cout << "ANTLRToken(ANTLRToken&&) -- move constructor\n";
        m_idx          = other.m_idx;
        m_token_type   = other.m_token_type;
        m_start_line   = other.m_start_line;
        m_start_column = other.m_start_column;
        m_end_line     = other.m_end_line;
        m_end_column   = other.m_end_column;
        // m_payload      = std::move(other.m_payload);

        std::ranges::copy(other.m_payload, std::back_inserter(m_payload));
        // other.m_payload = nullptr;
    }

    ANTLRToken &operator=(const ANTLRToken &other) {
        // std::cout << "ANTLRToken(ANTLRToken&&) -- copy assignment\n";
        m_idx          = other.m_idx;
        m_token_type   = other.m_token_type;
        m_start_line   = other.m_start_line;
        m_start_column = other.m_start_column;
        m_end_line     = other.m_end_line;
        m_end_column   = other.m_end_column;
        m_payload      = other.m_payload;

        return *this;
    }

    ANTLRToken(
        std::size_t idx, token_t token_type, std::size_t start_line, std::size_t start_column, std::size_t end_line,
        std::size_t end_column, std::string_view payload
    ) :
        m_idx(idx),
        m_token_type(token_type),
        m_start_line(start_line),
        m_start_column(start_column),
        m_end_line(end_line),
        m_end_column(end_column),
        m_payload(payload) {
    }

    std::string toString() const {
        return "[@" + std::to_string(m_idx) + "='" + m_payload.data() + "',<" + std::to_string(m_token_type) + ">," +
               std::to_string(m_start_line) + ":" + std::to_string(m_start_column - 1) + "]";
    }

    std::int16_t channel() const {
        return DEFAULT_CHANNEL;
    }

    std::size_t tokenIndex() const {
        return m_idx;
    }

    size_t getTokenIndex() const {
        return m_idx;
    }

    std::size_t line() const {
        return m_start_line;
    }

    std::size_t getLine() const {
        return m_start_line;
    }

    std::size_t column() const {
        return m_start_column - 1;
    }

    std::size_t getCharPositionInLine() const {
        return m_start_column - 1;
    }

    std::size_t getChannel() const {
        return DEFAULT_CHANNEL;
    }

    token_t type() const {
        return m_token_type;
    }

    std::size_t getType() const {
        return m_token_type;
    }

    std::string getText() const {
        return m_payload;
    }

    std::string getSource() const {
        return "";
    }

    void set_encoding(std::string_view enc) {
        ANTLRToken::encoding = enc;
    }

    void setText(std::string_view payload) {
        m_payload = payload;
    }

   private:

    std::size_t m_idx{};
    token_t     m_token_type{};
    std::size_t m_start_line{};
    std::size_t m_start_column{};
    std::size_t m_end_line{};
    std::size_t m_end_column{};
    std::string m_payload{};
};

class TokenFactory /*: public antlr4::TokenFactory<ANTLRToken>*/ {
   public:

    TokenFactory() = default;

    //~TokenFactory() noexcept = default;

    std::unique_ptr<ANTLRToken> create(
        std::string source, std::size_t type, const std::string &text, std::size_t channel, std::size_t start, std::size_t stop,
        std::size_t line, std::size_t column
    ) noexcept {
        return std::make_unique<ANTLRToken>(ANTLRToken(0, type, line, column, line, column, text));
    }

    std::unique_ptr<ANTLRToken> create(size_t type, const std::string &text) noexcept {
        return std::make_unique<ANTLRToken>(ANTLRToken(0, type, 0, 0, 0, 0, text));
    }
};

class TokenSource {
   public:

    TokenSource() {
        m_token_factory = TokenFactory();
    }

    const TokenFactory &getFactory() const noexcept {
        return m_token_factory;
    }

   private:

    TokenFactory m_token_factory;
};

class TokenReader {
   public:

    TokenReader(std::string_view fname) : m_file_name(fname), _p(0), _numMarkers{}, _currentTokenIndex{ 0 } {
        open();
        fill(1);
    }

    ~TokenReader() {
        close();
    }

    void dump_tokens() const noexcept {
        auto idx = 0;
        for (const auto &token : _tokens) {
            std::cout << "\t" << idx << " [" << token.toString() << "]" << std::endl;
            idx++;
        }
    }

    ANTLRToken *LT(std::int64_t i) {
        if (i == -1) {
            return &_lastToken;
        }

        sync(i);

        std::int64_t index = static_cast<std::int64_t>(_p) + i - 1;
        if (index < 0) {
            throw IndexOutOfBoundsException(std::string("LT(") + std::to_string(i) + std::string(") gives negative index"));
        }

        if (index >= static_cast<std::int64_t>(_tokens.size())) {
            // assert(_tokens.size() > 0 && _tokens.back()->type()) == ANTLRToken::EOF);
            return &_tokens.back();
        }

        return &_tokens[static_cast<std::size_t>(index)];
    }

    ANTLRToken::token_t LA(std::int64_t k) noexcept {
        return LT(k)->type();
    }

    void consume() {
        if (LA(1) == ANTLRToken::_EOF) {
            throw IllegalStateException("cannot consume EOF");
        }

        // buf always has at least tokens[p==0] in this method due to ctor
        _lastToken = _tokens[_p];  // track last token for LT(-1)

        // if we're at last token and no markers, opportunity to flush buffer
        if (_p == _tokens.size() - 1 && _numMarkers == 0) {
            _tokens.clear();
            _p                    = 0;
            _lastTokenBufferStart = _lastToken;
        } else {
            ++_p;
        }

        ++_currentTokenIndex;
        sync(1);
    }

    std::size_t mark() noexcept {
        if (_numMarkers == 0) {
            _lastTokenBufferStart = _lastToken;
        }

        int mark = -_numMarkers - 1;
        _numMarkers++;
        return mark;
    }

    void release(std::size_t marker) {
        if (const std::size_t expectedMark = -_numMarkers; marker != expectedMark) {
            throw IllegalStateException("release() called with an invalid marker.");
        }

        _numMarkers--;
        if (_numMarkers == 0) {  // can we release buffer?
            if (_p > 0) {
                // Copy tokens[p]..tokens[n-1] to tokens[0]..tokens[(n-1)-p], reset ptrs
                // p is last valid token; move nothing if p==n as we have no valid char
                _tokens.erase(_tokens.begin(), _tokens.begin() + _p);
                _p = 0;
            }
            _lastTokenBufferStart = _lastToken;
        }
    }

    std::size_t index() const noexcept {
        return _currentTokenIndex;
    }

    std::size_t getBufferStartIndex() const noexcept {
        return _currentTokenIndex - _p;
    }

    [[noreturn]] std::size_t size() const {
        throw UnsupportedOperationException("Size of stream is not known.");
    }

    [[noreturn]] ANTLRToken *get(size_t index) const {
        throw UnsupportedOperationException("get() operation not supported.");
    }

    [[noreturn]] TokenSource *getTokenSource() const {
        throw UnsupportedOperationException("getTokenSource() operation not supported.");
    }

    void seek(std::size_t index) {
        if (index == _currentTokenIndex) {
            return;
        }

        if (index > _currentTokenIndex) {
            sync(std::size_t(index - _currentTokenIndex));
            index = std::min(index, getBufferStartIndex() + _tokens.size() - 1);
        }

        std::size_t bufferStartIndex = getBufferStartIndex();
        if (bufferStartIndex > index) {
            throw IllegalArgumentException(std::string("cannot seek to negative index ") + std::to_string(index));
        }

        std::size_t i = index - bufferStartIndex;
        if (i >= _tokens.size()) {
            throw UnsupportedOperationException(
                std::string("seek to index outside buffer: ") + std::to_string(index) + " not in " +
                std::to_string(bufferStartIndex) + ".." + std::to_string(bufferStartIndex + _tokens.size())
            );
        }

        _p                 = i;
        _currentTokenIndex = index;
        if (_p == 0) {
            _lastToken = _lastTokenBufferStart;
        } else {
            _lastToken = _tokens[_p - 1];
        }
    }

    bool eof() const noexcept {
        return ::feof(m_file) != 0;
    }

    void open() {
    #if defined(_MSC_VER)
        auto err = ::fopen_s(&m_file, m_file_name.c_str(), "rb");
        if (err != 0) {
            throw std::runtime_error("Could not open file '" + m_file_name + "'.\n");
        }

    #else
        m_file = ::fopen(m_file_name.c_str(), "rb");
        if (m_file == nullptr) {
            throw std::runtime_error("Could not open file '" + m_file_name + "'.\n");
        }
    #endif
    }

    void close() noexcept {
        ::fclose(m_file);
    }

   protected:

    size_t fill(std::size_t n) {
        for (std::size_t i = 0; i < n; i++) {
            if (_tokens.size() > 0 && _tokens.back().type() == ANTLRToken::_EOF) {
                return i;
            }
            add(fetch_next());
        }
        return n;
    }

    void sync(std::size_t want) {
        std::size_t need = (static_cast<std::size_t>(_p) + want - 1) - static_cast<std::size_t>(_tokens.size()) + 1;
        if (need > 0) {
            fill(static_cast<std::size_t>(need));
        }
    }

    void add(const ANTLRToken &t) {
        _tokens.push_back(t);
    }

    ANTLRToken fetch_next() const {
        auto length     = read_int();
        auto token_type = read_int();
        auto start_line = read_int();
        auto start_col  = read_int();
        auto end_line   = read_int();
        auto end_col    = read_int();
        auto data       = read_string(length);

        if (eof()) {
            token_type = ANTLRToken::_EOF;
        }

        return ANTLRToken(_currentTokenIndex, token_type, start_line, start_col, end_line, end_col, data);
    }

    std::size_t read_int() const {
        std::size_t value = 0;

        ::fread((char *)&value, sizeof(std::size_t), 1, m_file);
        return value;
    }

    std::string read_string(std::size_t count) const {
        std::vector<char> buf(count + 1);

        ::fread(buf.data(), 1, count, m_file);
        buf[count] = '\x00';
        std::string result{ buf.data() };
        return result;
    }

   private:

    std::vector<ANTLRToken> _tokens;
    std::string             m_file_name;
    std::FILE              *m_file{ nullptr };
    size_t                  _p;
    int                     _numMarkers;
    ANTLRToken              _lastToken;
    ANTLRToken              _lastTokenBufferStart;
    size_t                  _currentTokenIndex;

    TokenSource m_source;
};

#endif  // __TOKEN_STREAM_HPP
