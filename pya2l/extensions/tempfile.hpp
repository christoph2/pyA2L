/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

    (C) 2023-2024 by Christoph Schueler <cpu12.gems.googlemail.com>

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

namespace fs = std::filesystem;

/*
 * Create ofstream object and delete on d-tor (or using 'remove()').
 */
class TempFile {
   public:

    explicit TempFile(const std::string& path, bool binary = false) :
        m_path(fs::path(path)),
        m_file(path, std::ios::trunc | std::ios::out | (binary ? std::ios::binary : std::ios::out)),
        m_closed(false) {
        if (!m_file.is_open()) {
            throw std::runtime_error("Could not open file '" + path + "'");
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
        // Mark the moved-from object as closed
        other.m_closed = true;
    }

    // Move assignment operator
    TempFile& operator=(TempFile&& other) noexcept {
        if (this != &other) {
            // Close current resources
            close();

            // Move resources from other
            m_path = std::move(other.m_path);
            m_file = std::move(other.m_file);
            m_closed = other.m_closed;

            // Mark the moved-from object as closed
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
            m_file.close();
            m_closed = true;
        }
    }

    std::string abs_path() const noexcept {
        return fs::absolute(m_path.string()).string();
    }

    void remove() noexcept {
        close();
        if (!m_closed && fs::exists(m_path)) {
            // fs::remove(m_path);
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
};

#endif  // __TEMPFILE_HPP
