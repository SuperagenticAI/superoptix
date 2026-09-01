#!/bin/sh
#
# SuperOptiX one-line installer for macOS, Linux, and WSL:
#
#   curl -fsSL https://superoptix.ai/install.sh | sh
#
# The script installs uv when it is missing, then uses uv to install SuperOptiX
# from PyPI in an isolated tool environment. It never uses sudo.
#
# Options, all passed as environment variables:
#
#   SUPEROPTIX_EXTRAS   comma separated extras, for example "frameworks-dspy,a2a"
#   SUPEROPTIX_VERSION  pin an exact version, for example "0.3.1"
#
#   curl -fsSL https://superoptix.ai/install.sh | SUPEROPTIX_EXTRAS=a2a sh

set -eu

UV_INSTALLER_URL="${SUPEROPTIX_UV_INSTALLER_URL:-https://astral.sh/uv/install.sh}"
SUPEROPTIX_EXTRAS_VALUE="${SUPEROPTIX_EXTRAS:-}"
SUPEROPTIX_VERSION_VALUE="${SUPEROPTIX_VERSION:-}"

find_uv() {
    if command -v uv >/dev/null 2>&1; then
        command -v uv
        return
    fi

    if [ -n "${UV_INSTALL_DIR:-}" ] && [ -x "${UV_INSTALL_DIR}/uv" ]; then
        printf '%s\n' "${UV_INSTALL_DIR}/uv"
        return
    fi

    if [ -n "${XDG_BIN_HOME:-}" ] && [ -x "${XDG_BIN_HOME}/uv" ]; then
        printf '%s\n' "${XDG_BIN_HOME}/uv"
        return
    fi

    if [ -n "${HOME:-}" ]; then
        for candidate in "${HOME}/.local/bin/uv" "${HOME}/.cargo/bin/uv"; do
            if [ -x "$candidate" ]; then
                printf '%s\n' "$candidate"
                return
            fi
        done
    fi

    return 1
}

install_uv() {
    printf '%s\n' "SuperOptiX uses uv to manage an isolated Python environment."
    printf '%s\n' "uv was not found, so the official Astral uv installer will run now."
    printf '%s\n' "Installer source: ${UV_INSTALLER_URL}"

    if command -v curl >/dev/null 2>&1; then
        curl -LsSf "$UV_INSTALLER_URL" | sh
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- "$UV_INSTALLER_URL" | sh
    else
        printf '%s\n' "Error: installing uv requires curl or wget." >&2
        exit 1
    fi
}

validate_options() {
    case "$SUPEROPTIX_EXTRAS_VALUE" in
        *[!A-Za-z0-9,_-]*)
            printf '%s\n' \
                "Error: SUPEROPTIX_EXTRAS may contain only letters, numbers, commas, '_' and '-'." \
                >&2
            exit 1
            ;;
    esac
    case "$SUPEROPTIX_VERSION_VALUE" in
        *[!A-Za-z0-9._+!-]*)
            printf '%s\n' "Error: SUPEROPTIX_VERSION contains unsupported characters." >&2
            exit 1
            ;;
    esac
}

validate_options

uv_bin="$(find_uv || true)"
if [ -z "$uv_bin" ]; then
    install_uv
    uv_bin="$(find_uv || true)"
fi

if [ -z "$uv_bin" ]; then
    printf '%s\n' "Error: uv was installed but its executable could not be found." >&2
    printf '%s\n' "Open a new terminal and run: uv tool install superoptix" >&2
    exit 1
fi

package_spec="superoptix"
if [ -n "$SUPEROPTIX_EXTRAS_VALUE" ]; then
    package_spec="${package_spec}[${SUPEROPTIX_EXTRAS_VALUE}]"
fi
if [ -n "$SUPEROPTIX_VERSION_VALUE" ]; then
    package_spec="${package_spec}==${SUPEROPTIX_VERSION_VALUE}"
fi

printf '%s\n' "Installing ${package_spec} from PyPI with ${uv_bin}..."
"$uv_bin" tool install \
    --no-config \
    --upgrade \
    --force \
    "$package_spec"

tool_bin="$("$uv_bin" tool dir --bin --no-config)"
super_bin="${tool_bin}/super"

if [ ! -x "$super_bin" ]; then
    printf '%s\n' "Error: SuperOptiX was installed but ${super_bin} was not found." >&2
    exit 1
fi

"$super_bin" --version

printf '%s\n' ""
printf '%s\n' "SuperOptiX is installed. The command is: super"
printf '%s\n' ""
printf '%s\n' "Adapt an agent you already run to A2A:"
printf '%s\n' "  super a2a adapt --entrypoint mymodule:agent --framework crewai"
printf '%s\n' ""
printf '%s\n' "Start a new project:"
printf '%s\n' "  super init myproject"
printf '%s\n' ""
printf '%s\n' "Docs: https://docs.superoptix.ai"
printf '%s\n' "Upgrade later by running this installer again."
printf '%s\n' "Uninstall with: ${uv_bin} tool uninstall superoptix"

case ":${PATH}:" in
    *":${tool_bin}:"*) ;;
    *)
        printf '%s\n' \
            "Restart your shell if 'super' is not found; ${tool_bin} must be on PATH."
        ;;
esac
