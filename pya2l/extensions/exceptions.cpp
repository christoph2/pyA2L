
#include "exceptions.hpp"

RuntimeException::RuntimeException(const std::string &msg) : std::exception(), _message(msg) {
}

const char* RuntimeException::what() const noexcept {
  return _message.c_str();
}


IllegalStateException::~IllegalStateException() {
}


IllegalArgumentException::~IllegalArgumentException() {
}


NullPointerException::~NullPointerException() {
}


IndexOutOfBoundsException::~IndexOutOfBoundsException() {
}


UnsupportedOperationException::~UnsupportedOperationException() {
}

