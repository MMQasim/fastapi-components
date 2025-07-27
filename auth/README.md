# 🔐 fastapi-components-auth

Reusable, modular **authentication service** for FastAPI applications using JWT tokens and pluggable user models.

This package is a submodule of the [`fastapi-components`](https://github.com/yourname/fastapi-components) monorepo, designed to be easily integrated into any FastAPI backend with minimal configuration.

---

## 🚀 Features

- ✅ Stateless JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ Dependency-injected user model compatibility
- ✅ Supports all user model types: flat, role-based, dynamic, or external
- ✅ Fully decoupled and testable

---

## 📦 Installation

Install from your local monorepo:

```bash
pip install -e ./auth
