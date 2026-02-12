/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

    (C) 2023-2026 by Christoph Schueler <cpu12.gems.googlemail.com>

    All Rights Reserved

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    s. FLOSS-EXCEPTION.txt
*/

#if !defined(__TEMPFILE_HPP)
    #define __TEMPFILE_HPP

    #include <filesystem>
    #include <fstream>
    #include <iostream>
    #include <stdexcept>
    #include <random>
    #include <chrono>
    #include <sstream>
    #include <thread>

namespace fs = std::filesystem;

/*
 *
 * Files are created in std::filesystem::temp_directory_path() with a unique name + suffix.
 *
 */
class TempFile {
   public:

    explicit TempFile(const std::string& suffix, bool binary = false) :
        m_path(create_unique_temp_path(suffix)),
        m_file(m_path, std::ios::trunc | std::ios::out | (binary ? std::ios::binary : static_cast<std::ios::openmode>(0))),
        m_closed(false) {
        if (!m_file.is_open()) {
            throw std::runtime_error("Could not open temporary file '" + m_path.string() + "'");
        }
    }

    // Delete default constructor
    TempFile() = delete;

    // Delete copy constructor
    TempFile(const TempFile&) = delete;

    // Delete copy assignment operator
    TempFile& operator=(const TempFile&) = delete;

    // Move constructor
    TempFile(TempFile&& other) noexcept :
        m_path(std::move(other.m_path)),
        m_file(std::move(other.m_file)),
        m_closed(other.m_closed) {
        other.m_closed = true;
    }

    // Move assignment operator
    TempFile& operator=(TempFile&& other) noexcept {
        if (this != &other) {
            close();
            m_path = std::move(other.m_path);
            m_file = std::move(other.m_file);
            m_closed = other.m_closed;
            other.m_closed = true;
        }
        return *this;
    }

    ~TempFile() noexcept {
        remove();
    }

    std::ofstream& operator()() noexcept {
        return m_file;
    }

    void close() noexcept {
        if (!m_closed && m_file.is_open()) {
            try {
                m_file.close();
            } catch (...) {
                // ignore
            }
            m_closed = true;
        }
    }

    std::string abs_path() const noexcept {
        try {
            return fs::absolute(m_path).string();
        } catch (...) {
            return m_path.string();
        }
    }

    void remove() noexcept {
        close();
        try {
            if (fs::exists(m_path)) {
                fs::remove(m_path);
            }
        } catch (...) {
            // suppress exceptions during cleanup
        }
    }

    void to_stdout() {
        // m_file.rdbuf(std::cout.rdbuf());
    }

    std::ofstream& handle() noexcept {
        return m_file;
    }

   private:

    fs::path      m_path;
    std::ofstream m_file;
    bool          m_closed;

    static fs::path create_unique_temp_path(const std::string& suffix) {
        const fs::path temp_dir = []() -> fs::path {
            try {
                return fs::temp_directory_path();
            } catch (...) {
                return fs::current_path();
            }
        }();

        // base name prefix
        const std::string prefix = "pya2l_";

        // random generator
        std::random_device rd;
        std::mt19937_64 gen(rd());
        std::uniform_int_distribution<uint64_t> dist;

        // try multiple times to avoid collision
        for (int attempt = 0; attempt < 16; ++attempt) {
            // timestamp
            const auto now = std::chrono::steady_clock::now().time_since_epoch().count();
            const uint64_t rnd = dist(gen);
            std::ostringstream oss;
            oss << prefix << std::hex << now << "_" << rnd << suffix;
            fs::path candidate = temp_dir / oss.str();

            // Try to create the file atomically by opening with std::ofstream with trunc.
            // If creation succeeds, remove it immediately and return the path (we will open again in ctor).
            // To ensure exclusivity, attempt to open exclusively by checking existence beforehand and after opening.
            try {
                if (!fs::exists(candidate)) {
                    // attempt to create file
                    std::ofstream ofs(candidate, std::ios::out | std::ios::app);
                    if (ofs.is_open()) {
                        ofs.close();
                        return candidate;
                    }
                }
            } catch (...) {
                // ignore and try next
            }
            // small backoff
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }
        throw std::runtime_error("Failed to create unique temporary filename with suffix '" + suffix + "'");
    }
};

#endif  // __TEMPFILE_HPP
