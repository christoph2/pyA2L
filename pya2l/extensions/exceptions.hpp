
#if !defined(__EXCEPTIONS_HPP)
    #define __EXCEPTIONS_HPP

    #include <stdexcept>
    #include <string>

class RuntimeException : public std::exception {
   private:

    std::string _message;

   public:

    RuntimeException(std::string msg = "");

    const char* what() const noexcept override;
};

class UnsupportedOperationException : public RuntimeException {
   public:

    UnsupportedOperationException(const std::string& msg = "") : RuntimeException(msg) {
    }

    UnsupportedOperationException(UnsupportedOperationException const &) = default;
    ~UnsupportedOperationException() override;
    UnsupportedOperationException& operator=(UnsupportedOperationException const &) = default;
};

class IllegalStateException : public RuntimeException {
   public:

    IllegalStateException(const std::string& msg = "") : RuntimeException(msg) {
    }

    IllegalStateException(IllegalStateException const &) = default;
    ~IllegalStateException() override;
    IllegalStateException& operator=(IllegalStateException const &) = default;
};

class IllegalArgumentException : public RuntimeException {
   public:

    IllegalArgumentException(IllegalArgumentException const &) = default;

    IllegalArgumentException(const std::string& msg = "") : RuntimeException(msg) {
    }

    ~IllegalArgumentException() override;
    IllegalArgumentException& operator=(IllegalArgumentException const &) = default;
};

class NullPointerException : public RuntimeException {
   public:

    NullPointerException(const std::string& msg = "") : RuntimeException(msg) {
    }

    NullPointerException(NullPointerException const &) = default;
    ~NullPointerException() override;
    NullPointerException& operator=(NullPointerException const &) = default;
};

class IndexOutOfBoundsException : public RuntimeException {
   public:

    IndexOutOfBoundsException(const std::string& msg = "") : RuntimeException(msg) {
    }

    IndexOutOfBoundsException(IndexOutOfBoundsException const &) = default;
    ~IndexOutOfBoundsException() override;
    IndexOutOfBoundsException& operator=(IndexOutOfBoundsException const &) = default;
};

#endif  // __EXCEPTIONS_HPP
