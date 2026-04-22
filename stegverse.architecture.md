{
  "$schema": "https://stegverse.org/schemas/architecture_manifest.schema.json",
  "schema_version": "1.0.0",
  "repo_id": "StegVerse-SDK",
  "repo_type": "sdk",
  "description": "StegVerse SDK -- user-facing interface to the Trust Kernel. Provides runtime governance for autonomous systems by enforcing decision verification at the execution boundary.",
  "inherits_from": null,
  "enforcement": "strict",
  
  "expected_structure": {
    "docs/architecture/ARCHITECTURE.md": {
      "required": true,
      "purpose": "Canonical architecture documentation"
    },
    "docs/architecture/decisions/": {
      "required": true,
      "purpose": "Architecture Decision Records"
    },
    "docs/api/": {
      "required": false,
      "purpose": "Generated API docs"
    },
    "docs/guides/": {
      "required": false,
      "purpose": "User guides and tutorials"
    },
    "stegverse/": {
      "required": true,
      "purpose": "Main Python package",
      "subdirs": {
        "__init__.py": {
          "required": true,
          "purpose": "Package init -- exports public API"
        },
        "core/": {
          "required": false,
          "purpose": "Trust Kernel client, session management",
          "subdirs": {
            "__init__.py": { "required": true },
            "client.py": {
              "required": false,
              "purpose": "Main Trust Kernel client"
            },
            "kernel_api.py": {
              "required": false,
              "purpose": "Kernel API interface"
            },
            "session.py": {
              "required": false,
              "purpose": "Session lifecycle"
            },
            "config.py": {
              "required": false,
              "purpose": "Configuration"
            }
          }
        },
        "adapters/": {
          "required": false,
          "purpose": "Platform bindings -- LLM adapters, CLI, async",
          "subdirs": {
            "__init__.py": { "required": true },
            "llm_adapter_dual.py": {
              "required": false,
              "purpose": "Dual-mode LLM adapter"
            },
            "sync.py": {
              "required": false,
              "purpose": "Synchronous adapter"
            },
            "async_.py": {
              "required": false,
              "purpose": "Asynchronous adapter"
            },
            "cli.py": {
              "required": false,
              "purpose": "Command-line interface"
            }
          }
        },
        "governance/": {
          "required": false,
          "purpose": "Policy engine, admission control, safety stack",
          "subdirs": {
            "__init__.py": { "required": true },
            "safety_stack.py": {
              "required": false,
              "purpose": "Safety and governance stack"
            },
            "policy.py": {
              "required": false,
              "purpose": "Policy definitions"
            },
            "admission.py": {
              "required": false,
              "purpose": "Admission control"
            },
            "constraints.py": {
              "required": false,
              "purpose": "Constraint evaluation"
            },
            "rules/": {
              "required": false,
              "purpose": "Built-in governance rules"
            }
          }
        },
        "receipts/": {
          "required": false,
          "purpose": "Receipt generation, validation, chain linking",
          "subdirs": {
            "__init__.py": { "required": true },
            "receipts.py": {
              "required": false,
              "purpose": "Receipt operations"
            },
            "generator.py": {
              "required": false,
              "purpose": "Receipt creation"
            },
            "validator.py": {
              "required": false,
              "purpose": "Receipt validation"
            },
            "chain.py": {
              "required": false,
              "purpose": "Receipt chain linking"
            },
            "store.py": {
              "required": false,
              "purpose": "Receipt persistence"
            }
          }
        },
        "schemas/": {
          "required": true,
          "purpose": "JSON/YAML schemas for validation"
        },
        "exceptions.py": {
          "required": false,
          "purpose": "Custom exception hierarchy"
        },
        "types.py": {
          "required": false,
          "purpose": "Shared type definitions"
        },
        "utils/": {
          "required": false,
          "purpose": "Internal utilities",
          "subdirs": {
            "__init__.py": { "required": true }
          }
        }
      }
    },
    "tests/": {
      "required": true,
      "purpose": "Test suite",
      "subdirs": {
        "unit/": {
          "required": false,
          "purpose": "Unit tests"
        },
        "integration/": {
          "required": false,
          "purpose": "Integration tests"
        },
        "fixtures/": {
          "required": false,
          "purpose": "Test data and mocks"
        },
        "conftest.py": {
          "required": false,
          "purpose": "pytest shared fixtures"
        }
      }
    },
    "examples/": {
      "required": true,
      "purpose": "Runnable demonstrations"
    },
    "scripts/": {
      "required": false,
      "purpose": "Build and maintenance scripts"
    },
    "requirements.txt": {
      "required": true,
      "purpose": "Runtime dependencies"
    },
    "requirements-dev.txt": {
      "required": false,
      "purpose": "Development dependencies"
    },
    "setup.py": {
      "required": false,
      "purpose": "Legacy packaging (deprecated, use pyproject.toml)"
    },
    "pyproject.toml": {
      "required": true,
      "purpose": "Modern Python packaging"
    },
    "README.md": {
      "required": true,
      "purpose": "Project overview and quickstart"
    },
    "LICENSE": {
      "required": true,
      "purpose": "Software license"
    },
    "CHANGELOG.md": {
      "required": false,
      "purpose": "Version history"
    },
    "CONTRIBUTING.md": {
      "required": false,
      "purpose": "Contributor guidelines"
    },
    ".github/workflows/": {
      "required": true,
      "purpose": "CI/CD workflows"
    },
    ".github/ISSUE_TEMPLATE/": {
      "required": false,
      "purpose": "Issue templates"
    },
    ".pre-commit-config.yaml": {
      "required": false,
      "purpose": "Pre-commit hooks"
    }
  },

  "file_rules": {
    "naming_conventions": {
      "python_modules": "snake_case",
      "python_packages": "snake_case",
      "classes": "PascalCase",
      "functions": "snake_case",
      "constants": "UPPER_SNAKE_CASE",
      "test_files": "test_*.py",
      "private_modules": "_*.py"
    },
    "forbidden_patterns": [
      ".*secret.*\\.py$",
      ".*password.*",
      ".*api_key.*\\.txt$",
      ".*private_key.*",
      "\\.env$",
      "\\.env\\..*",
      "\\.pyc$",
      "__pycache__",
      ".*\\.bak$",
      ".*\\.tmp$",
      ".*\\.swp$",
      ".*~$"
    ],
    "required_extensions": {
      "python_source": [".py"],
      "documentation": [".md", ".rst"],
      "schemas": [".json", ".yaml", ".yml"],
      "configs": [".toml", ".cfg", ".ini"]
    }
  },

  "migration_rules": {
    "review_needed_path": "review_needed/",
    "legacy_path": "legacy/",
    "wiring_path": "wiring/",
    "auto_migrate": false,
    "require_approval": true,
    "syntax_issue_patterns": [
      ".*\\s+.*",
      ".*[^a-zA-Z0-9_\\-\\./].*",
      ".*\\.\\..*",
      ".*\\.\\.$"
    ]
  },

  "validation_hooks": {
    "pre_commit": true,
    "ci_pull_request": true,
    "ci_push_main": true,
    "scheduled_audit": "weekly"
  },

  "integration_points": {
    "stegbrain": "github.com/StegVerse-Labs/StegBrain",
    "tv": "github.com/StegVerse-Labs/TV",
    "tvc": "github.com/StegVerse-Labs/TVC",
    "entity_sandbox": "github.com/StegVerse-Labs/entity-sandbox",
    "demo_suite": "github.com/StegVerse-org/stegverse-demo-suite",
    "gsl": "github.com/StegVerse-org/stegverse-gsl"
  }
}
