
#if !defined(__EXCEPTIONS_HPP)
    #define __EXCEPTIONS_HPP

    #include <stdexcept>

class RuntimeException : public std::exception {
   private:

    std::string _message;

   public:

    RuntimeException(const std::string& msg = "");

    const char* what() const noexcept override;
};

class UnsupportedOperationException : public RuntimeException {
   public:

    UnsupportedOperationException(const std::string& msg = "") : RuntimeException(msg) {
    }

    UnsupportedOperationException(UnsupportedOperationException const &) = default;
    ~UnsupportedOperationException();
    UnsupportedOperationException& operator=(UnsupportedOperationException const &) = default;
};

class IllegalStateException : public RuntimeException {
   public:

    IllegalStateException(const std::string& msg = "") : RuntimeException(msg) {
    }

    IllegalStateException(IllegalStateException const &) = default;
    ~IllegalStateException();
    IllegalStateException& operator=(IllegalStateException const &) = default;
};

class IllegalArgumentException : public RuntimeException {
   public:

    IllegalArgumentException(IllegalArgumentException const &) = default;

    IllegalArgumentException(const std::string& msg = "") : RuntimeException(msg) {
    }

    ~IllegalArgumentException();
    IllegalArgumentException& operator=(IllegalArgumentException const &) = default;
};

class NullPointerException : public RuntimeException {
   public:

    NullPointerException(const std::string& msg = "") : RuntimeException(msg) {
    }

    NullPointerException(NullPointerException const &) = default;
    ~NullPointerException();
    NullPointerException& operator=(NullPointerException const &) = default;
};

class IndexOutOfBoundsException : public RuntimeException {
   public:

    IndexOutOfBoundsException(const std::string& msg = "") : RuntimeException(msg) {
    }

    IndexOutOfBoundsException(IndexOutOfBoundsException const &) = default;
    ~IndexOutOfBoundsException();
    IndexOutOfBoundsException& operator=(IndexOutOfBoundsException const &) = default;
};

#endif  // __EXCEPTIONS_HPP
