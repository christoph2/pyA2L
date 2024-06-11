/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

    (C) 2023 by Christoph Schueler <cpu12.gems.googlemail.com>

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

#if !defined(__GENERATOR_HPP)
    #define __GENERATOR_HPP

    #include <array>
    #include <cassert>
    #include <cctype>
    #include <coroutine>
    #include <fstream>
    #include <future>
    #include <iostream>
    #include <sstream>
    #include <tuple>
    #include <variant>
    #include <vector>

/*
**  Basic c++20 generator implementation.
*/
template<typename Ty_>
struct Generator {
    /*
    ** Promise implementation.
    */
    struct promise_type : std::promise<Ty_> {
        Ty_ m_val;

        Generator get_return_object() noexcept {
            return this;
        }

        std::suspend_never initial_suspend() const noexcept {
            return {};
        }

        std::suspend_always final_suspend() noexcept(true) {
            return {};
        }

        std::suspend_always yield_value(const Ty_& val) noexcept {
            m_val = val;
            return {};
        }

        void return_void() {
        }

        void unhandled_exception() {
        }
    };

    /*
    ** Iterator implementation.
    */
    struct iterator {
        bool operator!=(const iterator& rhs) const noexcept {
            return !m_h_ptr->done();
        }

        iterator& operator++() noexcept {
            m_h_ptr->resume();
            return *this;
        }

        Ty_ operator*() noexcept {
            return m_h_ptr->promise().m_val;
        }

        std::coroutine_handle<promise_type>* m_h_ptr;
    };

    iterator begin() noexcept {
        return iterator{ &m_handle };
    }

    iterator end() const noexcept {
        return iterator{ nullptr };
    }

    Generator(promise_type* p) : m_handle(std::coroutine_handle<promise_type>::from_promise(*p)) {
    }

    ~Generator() {
        m_handle.destroy();
    }

    std::coroutine_handle<promise_type> m_handle;
};

#endif  // __GENERATOR_HPP
