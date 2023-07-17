
#if !defined(__TOKEN_STREAM_HPP)
    #define __TOKEN_STREAM_HPP

    #define __STDC_WANT_LIB_EXT1__ (1)
    #include <cstdio>
    #include <deque>

    #include "tempfile.hpp"
    #include "tokenizer.hpp"

template<typename Ty_>
class FixedSizeStack {
   public:

    FixedSizeStack(std::size_t size) : m_stack{}, m_size(size) {
    }

    FixedSizeStack(const FixedSizeStack&)            = delete;
    FixedSizeStack& operator=(const FixedSizeStack&) = delete;
    FixedSizeStack(FixedSizeStack&&)                 = delete;
    FixedSizeStack& operator=(FixedSizeStack&&)      = delete;

    ~FixedSizeStack() {
    }

    void push(const Ty_& value) noexcept {
        m_stack.push_front(value);
        if (m_stack.size() > m_size) {
            m_stack.pop_back();
        }
    }

    const Ty_& operator[](std::size_t index) {
        return m_stack[index];
    }

   private:

    std::deque<Ty_> m_stack;
    std::size_t     m_size;
};

class TokenWriter {
   public:

    const std::size_t HEADER_SIZE = sizeof(std::size_t) * (6);

    TokenWriter() = delete;

    TokenWriter(TempFile& outf) : m_outf(outf.handle()) {
    }

    void operator<<(const Token& token) {
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

    void write_int(std::size_t value) {
        std::size_t before = m_outf.tellp();
        m_outf.write(std::bit_cast<const char*>(&value), sizeof std::size_t);
        std::size_t after   = m_outf.tellp();
        std::size_t correct = before + 8;
        assert(correct == after);
    }

    void write_string(std::string_view text) {
        m_outf.write(text.data(), std::size(text));
    }

   private:

    std::ofstream& m_outf;
};

/*
Lexer implements interface TokenSource, which specifies the core lexer function-
ality: nextToken(), getLine(), and getCharPositionInLine(). Rolling our own lexer to use
with an ANTLR parser grammar is not too much work. Let’s build a lexer that
tokenizes simple identifiers and integers like the following input file:

@Override
public Token nextToken() {
    while (true) {
        if ( c==(char)CharStream.EOF ) return createToken(Token.EOF);
        while ( Character.isWhitespace(c) ) consume(); // toss out whitespace
        startCharIndex = input.index();
        startLine = getLine();
        startCharPositionInLine = getCharPositionInLine();
        if ( c==';' ) {
            consume();
            return createToken(SEMI);
        } else if ( c>='0' && c<='9' ) {
            while ( c>='0' && c<='9' ) consume();
            return createToken(INT);
        } else if ( c>='a' && c<='z' ) { // VERY simple ID
        while ( c>='a' && c<='z' ) consume();
        return createToken(ID);
    }
    // error; consume and try again
    consume();
    }
}

protected Token createToken(int ttype) {
    String text = null; // we use start..stop indexes in input
    Pair<TokenSource, CharStream> source = new Pair<TokenSource, CharStream>(this, input);

    return factory.create(source, ttype, text, Token.DEFAULT_CHANNEL, startCharIndex, input.index()-1, startLine,
startCharPositionInLine);
}

protected void consume() {
    if ( c=='\n' ) {
        line++;
        // \r comes back as a char, but \n means line++
        charPositionInLine = 0;
    }
    if ( c!=(char)CharStream.EOF ) input.consume();
    c = (char)input.LA(1);
    charPositionInLine++;
 }

*/

class ANTLRToken {
   public:

    using token_t = std::int16_t;

    static constexpr std::int16_t DEFAULT_CHANNEL     = 0;
    static constexpr token_t      _EOF                = -1;
    static constexpr token_t      EPSILON             = -2;
    static constexpr std::int16_t HIDDEN_CHANNEL      = 1;
    static constexpr token_t      INVALID_TYPE        = 0;
    static constexpr token_t      MIN_USER_TOKEN_TYPE = 1;

    ANTLRToken()                  = default;
    ANTLRToken(const ANTLRToken&) = default;

    ANTLRToken& operator=(const ANTLRToken& other) {
        m_idx          = other.m_idx;
        m_token_type   = other.m_token_type;
        m_start_line   = other.m_start_line;
        m_start_column = other.m_start_column;
        m_end_line     = other.m_end_line;
        m_end_column   = other.m_end_column;
        m_payload      = other.m_payload;

        return *this;
    }

    ~ANTLRToken() {
        // std::cout << "d-tor -- ANTLRToken() '" << m_payload << "'\n";
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

    std::string to_string() const {
        // [@0,0:12='ASAP2_VERSION',<49>,1:0]
        return "[@" + std::to_string(m_idx) + "='" + m_payload.data() + "',<" + std::to_string(m_token_type) + ">," +
               std::to_string(m_start_line) + ":" + std::to_string(m_start_column - 1) + "]";
    }

    std::int16_t channel() const {
        return DEFAULT_CHANNEL;
    }

    std::size_t tokenIndex() const {
        return m_idx;
    }

    std::size_t line() const {
        return m_start_line;
    }

    std::size_t column() const {
        return m_start_column - 1;
    }

    token_t type() const {
        return m_token_type;
    }

    auto getText() const {
        return m_payload;
    }

    std::string getSource() const {
        return "";
    }

    void setText(std::string_view payload) {
        m_payload = payload;
    }

    std::optional<std::size_t> start() const {
        return std::nullopt;
    }

    std::optional<std::size_t> stop() const {
        return std::nullopt;
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

class TokenFactory {
   public:

    TokenFactory() = default;

    ANTLRToken create(
        std::string source, ANTLRToken::token_t type, std::string text, std::int64_t channel, std::int64_t start, std::int64_t stop,
        std::int64_t line, std::int64_t column
    ) {
        return ANTLRToken(0, type, line, column, line, column, text);
    }
};

class TokenSource {
   public:

    TokenSource() {
        m_token_factory = TokenFactory();
    }

    const TokenFactory& getFactory() const {
        return m_token_factory;
    }

   private:

    TokenFactory m_token_factory;
};

class TokenReader {
   public:

    TokenReader(std::string_view fname) :
        m_file_name(fname), m_idx(0), m_token{}, m_la2_token{}, m_la2_token_valid{ false }, m_stack{ 16 }, m_source{} {
        open();
        m_token = fetch_next();
        update_tokens(m_token);
    }

    ~TokenReader() {
        close();
    }

    std::optional<ANTLRToken> LT(std::int64_t k) {
        std::cout << "\t\tLT(" << k << ")\n";
        if (k == 1) {
            std::cout << "\t\t\ttype: " << m_token.type() << "\n";
            return m_token;
        } else if (k == -1) {
            if (m_idx > 0) {
                std::cout << "\t\t\ttype: " << m_stack[1].type() << "\n";
                return m_stack[1];
            } else {
                std::cout << "\t@the beginning!!!\n";
                return std::nullopt;
            }
        } else {
            std::cout << "\tCannot handle yet!!!\n";
        }
        return std::nullopt;
    }

    std::optional<ANTLRToken::token_t> LA(std::int64_t k) {
        std::cout << "\t\tLA(" << k << ") ty: ";
        if (k == 1) {
            std::cout << m_token.type() << "\n";
            return m_token.type();
        } else if (k == 2) {
            if (!m_la2_token_valid) {
                m_la2_token       = fetch_next();
                m_la2_token_valid = true;
            }
            std::cout << m_la2_token.type() << "\n";
            return m_la2_token.type();
        } else {
            std::cout << "\t\t\tCould not satisfy!!!: " << k << "\n";
            // throw std::runtime_error("\t\t\tCould not satisfy!!!\n");
            return std::nullopt;
        }
    }

    void consume() {
        std::cout << "consume() " << m_la2_token_valid << "\n";

        if (m_la2_token_valid) {
            m_token = m_la2_token;
        } else {
            m_token = fetch_next();
        }

        update_tokens(m_token);
        m_la2_token_valid = false;
    }

    std::size_t mark() {
        std::cout << "mark()\n";
        return m_idx;
    }

    void release(std::size_t k) {
        std::cout << "mark(" << k << ")\n";
    }

    std::size_t getIndex() const {
        std::cout << "getIndex(" << m_idx << ")\n";
        return m_idx;
    }

    void seek(std::size_t k) {
        std::cout << "seek(" << k << ") !!!\n";
        if (k != m_idx) {
            std::cout << "\tk != idx !!!\n";
        }
    }

    bool eof() const {
        return ::feof(m_file) != 0;
    }

    void open() {
    #if defined(_MSC_VER)
        auto err = ::fopen_s(&m_file, m_file_name.c_str(), "rb");
        std::cout << "Err: " << err << "\n";
    #else
        m_file = ::fopen(m_file_name.c_str(), "rb");
    #endif
    }

    void close() {
        ::fclose(m_file);
    }

    const TokenSource& getTokenSource() const {
        return m_source;
    }

   protected:

    ANTLRToken fetch_next() const {
        auto length     = read_int();
        auto token_type = read_int();
        auto start_line = read_int();
        auto start_col  = read_int();
        auto end_line   = read_int();
        auto end_col    = read_int();
        auto data       = read_string(length);

        if (eof()) {
            std::cout << "\t*** EOF ***\n\n";
            token_type = ANTLRToken::_EOF;
        }

        auto token = ANTLRToken(m_idx, token_type, start_line, start_col, end_line, end_col, data);
        std::cout << "\t" << token.to_string() << "\n";

        return token;
    }

    void update_tokens(const ANTLRToken& token) {
        m_idx++;
        m_stack.push(token);
    }

    std::size_t read_int() const {
        std::size_t value = 0;

        ::fread((char*)&value, sizeof(std::size_t), 1, m_file);
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

    std::string                m_file_name;
    std::FILE*                 m_file{ nullptr };
    std::size_t                m_idx;
    ANTLRToken                 m_token;
    ANTLRToken                 m_la2_token;
    bool                       m_la2_token_valid;
    FixedSizeStack<ANTLRToken> m_stack;
    TokenSource                m_source;
};

#endif  // __TOKEN_STREAM_HPP
