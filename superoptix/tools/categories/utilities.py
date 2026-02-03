"""
SuperOptiX Utility Tools
========================

General-purpose utility tools for various tasks.
"""

import hashlib
import re
import secrets
import string


class PasswordGeneratorTool:
    """Secure password generation tool."""

    def generate_password(self, length: int = 12, include_symbols: bool = True) -> str:
        """Generate a secure random password."""
        try:
            if length < 4:
                return "❌ Password length must be at least 4 characters"

            if length > 128:
                return "❌ Password length cannot exceed 128 characters"

            # Character sets
            lowercase = string.ascii_lowercase
            uppercase = string.ascii_uppercase
            digits = string.digits
            symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if include_symbols else ""

            # Ensure at least one character from each required set
            password_chars = [
                secrets.choice(lowercase),
                secrets.choice(uppercase),
                secrets.choice(digits),
            ]

            if include_symbols and symbols:
                password_chars.append(secrets.choice(symbols))

            # Fill remaining length with random characters from all sets
            all_chars = lowercase + uppercase + digits + symbols
            for _ in range(length - len(password_chars)):
                password_chars.append(secrets.choice(all_chars))

            # Shuffle the password characters
            secrets.SystemRandom().shuffle(password_chars)
            password = "".join(password_chars)

            # Analyze password strength
            strength_score = 0
            strength_factors = []

            if len(password) >= 12:
                strength_score += 25
                strength_factors.append("✅ Good length (12+ chars)")
            elif len(password) >= 8:
                strength_score += 15
                strength_factors.append("⚠️  Moderate length (8-11 chars)")
            else:
                strength_factors.append("❌ Short length (<8 chars)")

            if any(c.islower() for c in password):
                strength_score += 10
                strength_factors.append("✅ Contains lowercase")

            if any(c.isupper() for c in password):
                strength_score += 10
                strength_factors.append("✅ Contains uppercase")

            if any(c.isdigit() for c in password):
                strength_score += 10
                strength_factors.append("✅ Contains numbers")

            if any(c in symbols for c in password):
                strength_score += 15
                strength_factors.append("✅ Contains symbols")

            # Variety bonus
            unique_chars = len(set(password))
            if unique_chars >= length * 0.8:
                strength_score += 20
                strength_factors.append("✅ High character variety")
            elif unique_chars >= length * 0.6:
                strength_score += 10
                strength_factors.append("⚠️  Moderate character variety")

            strength_level = (
                "Weak"
                if strength_score < 50
                else "Moderate"
                if strength_score < 80
                else "Strong"
            )

            return f"""🔐 Password Generated:
{"=" * 50}
Password: {password}
Length: {length} characters
Includes Symbols: {"Yes" if include_symbols else "No"}

Strength Analysis:
Level: {strength_level} ({strength_score}/100)

Factors:
{chr(10).join(strength_factors)}

Security Tips:
- Use unique passwords for each account
- Store securely (password manager recommended)
- Change regularly for sensitive accounts
"""
        except Exception as e:
            return f"❌ Password generation error: {str(e)}"


class HashGeneratorTool:
    """Hash generation and verification tool."""

    def generate_hash(self, text: str, algorithm: str = "sha256") -> str:
        """Generate hash for text using specified algorithm."""
        try:
            algorithm = algorithm.lower()

            # Supported algorithms
            hash_functions = {
                "md5": hashlib.md5,
                "sha1": hashlib.sha1,
                "sha256": hashlib.sha256,
                "sha512": hashlib.sha512,
            }

            if algorithm not in hash_functions:
                return f"❌ Unsupported algorithm. Available: {list(hash_functions.keys())}"

            # Generate hash
            hash_function = hash_functions[algorithm]
            hash_object = hash_function(text.encode("utf-8"))
            hash_hex = hash_object.hexdigest()

            # Security information
            security_info = {
                "md5": "⚠️  MD5 is cryptographically broken - avoid for security purposes",
                "sha1": "⚠️  SHA1 is deprecated - avoid for new applications",
                "sha256": "✅ SHA256 is secure and recommended",
                "sha512": "✅ SHA512 is secure and recommended",
            }

            return f"""🔢 Hash Generated:
{"=" * 50}
Input Text: {text[:50]}{"..." if len(text) > 50 else ""}
Algorithm: {algorithm.upper()}
Hash: {hash_hex}

Hash Length: {len(hash_hex)} characters
Security: {security_info.get(algorithm, "Unknown")}

Use Cases:
- Data integrity verification
- Password storage (with salt)
- Digital signatures
- Blockchain applications
"""
        except Exception as e:
            return f"❌ Hash generation error: {str(e)}"


class ColorConverterTool:
    """Color format conversion tool."""

    def convert_color(self, color_value: str, from_format: str, to_format: str) -> str:
        """Convert color between different formats."""
        try:
            from_format = from_format.lower()
            to_format = to_format.lower()

            # Parse input color
            if from_format == "hex":
                # Remove # if present
                hex_color = color_value.lstrip("#")
                if len(hex_color) != 6:
                    return "❌ Invalid hex color format. Use #RRGGBB or RRGGBB"

                try:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                except ValueError:
                    return "❌ Invalid hex color values"

            elif from_format == "rgb":
                # Parse RGB format like "255,128,0" or "rgb(255,128,0)"
                rgb_match = re.search(r"(\d+)[,\s]+(\d+)[,\s]+(\d+)", color_value)
                if not rgb_match:
                    return "❌ Invalid RGB format. Use 'r,g,b' or 'rgb(r,g,b)'"

                r, g, b = map(int, rgb_match.groups())
                if not all(0 <= val <= 255 for val in [r, g, b]):
                    return "❌ RGB values must be between 0 and 255"

            else:
                return "❌ Unsupported input format. Use 'hex' or 'rgb'"

            # Convert to target format
            result = ""
            if to_format == "hex":
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                result = hex_color

            elif to_format == "rgb":
                result = f"rgb({r}, {g}, {b})"

            elif to_format == "hsl":
                # Convert RGB to HSL
                r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
                max_val = max(r_norm, g_norm, b_norm)
                min_val = min(r_norm, g_norm, b_norm)

                h, s, l = 0, 0, (max_val + min_val) / 2

                if max_val == min_val:
                    h = s = 0  # achromatic
                else:
                    d = max_val - min_val
                    s = (
                        d / (2 - max_val - min_val)
                        if l > 0.5
                        else d / (max_val + min_val)
                    )

                    if max_val == r_norm:
                        h = (g_norm - b_norm) / d + (6 if g_norm < b_norm else 0)
                    elif max_val == g_norm:
                        h = (b_norm - r_norm) / d + 2
                    elif max_val == b_norm:
                        h = (r_norm - g_norm) / d + 4
                    h /= 6

                h = int(h * 360)
                s = int(s * 100)
                l = int(l * 100)
                result = f"hsl({h}, {s}%, {l}%)"

            else:
                return "❌ Unsupported output format. Use 'hex', 'rgb', or 'hsl'"

            return f"""🎨 Color Conversion:
{"=" * 50}
Input: {color_value} ({from_format.upper()})
Output: {result} ({to_format.upper()})

RGB Values: R={r}, G={g}, B={b}
Hex: #{r:02x}{g:02x}{b:02x}

Color Preview:
████████ (Imagine this in the actual color!)

Use Cases:
- Web design and CSS
- Graphic design applications
- Color palette development
"""
        except Exception as e:
            return f"❌ Color conversion error: {str(e)}"


class UnitConverterTool:
    """Unit conversion tool for various measurement types."""

    def __init__(self):
        # Conversion factors to base units
        self.conversions = {
            "length": {
                "meter": 1.0,
                "kilometer": 1000.0,
                "centimeter": 0.01,
                "millimeter": 0.001,
                "inch": 0.0254,
                "foot": 0.3048,
                "yard": 0.9144,
                "mile": 1609.34,
            },
            "weight": {
                "gram": 1.0,
                "kilogram": 1000.0,
                "pound": 453.592,
                "ounce": 28.3495,
                "ton": 1000000.0,
            },
            "temperature": {
                # Special handling required
            },
            "volume": {
                "liter": 1.0,
                "milliliter": 0.001,
                "gallon": 3.78541,
                "quart": 0.946353,
                "pint": 0.473176,
                "cup": 0.236588,
                "fluid_ounce": 0.0295735,
            },
        }

    def convert_unit(
        self, value: float, from_unit: str, to_unit: str, unit_type: str
    ) -> str:
        """Convert units within a measurement type."""
        try:
            unit_type = unit_type.lower()
            from_unit = from_unit.lower()
            to_unit = to_unit.lower()

            if unit_type == "temperature":
                return self._convert_temperature(value, from_unit, to_unit)

            if unit_type not in self.conversions:
                return f"❌ Unsupported unit type. Available: {list(self.conversions.keys())}"

            unit_dict = self.conversions[unit_type]

            if from_unit not in unit_dict:
                return f"❌ Unknown source unit '{from_unit}' for {unit_type}"

            if to_unit not in unit_dict:
                return f"❌ Unknown target unit '{to_unit}' for {unit_type}"

            # Convert to base unit, then to target unit
            base_value = value * unit_dict[from_unit]
            result_value = base_value / unit_dict[to_unit]

            return f"""📏 Unit Conversion:
{"=" * 50}
{value} {from_unit} = {result_value:.6g} {to_unit}

Conversion Type: {unit_type.title()}
Conversion Factor: 1 {from_unit} = {unit_dict[from_unit] / unit_dict[to_unit]:.6g} {to_unit}
"""
        except Exception as e:
            return f"❌ Unit conversion error: {str(e)}"

    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> str:
        """Convert temperature between Celsius, Fahrenheit, and Kelvin."""
        try:
            # Convert to Celsius first
            if from_unit == "fahrenheit":
                celsius = (value - 32) * 5 / 9
            elif from_unit == "kelvin":
                celsius = value - 273.15
            elif from_unit == "celsius":
                celsius = value
            else:
                return f"❌ Unknown temperature unit '{from_unit}'. Use celsius, fahrenheit, or kelvin"

            # Convert from Celsius to target
            if to_unit == "celsius":
                result = celsius
            elif to_unit == "fahrenheit":
                result = celsius * 9 / 5 + 32
            elif to_unit == "kelvin":
                result = celsius + 273.15
            else:
                return f"❌ Unknown temperature unit '{to_unit}'. Use celsius, fahrenheit, or kelvin"

            return f"""🌡️ Temperature Conversion:
{"=" * 50}
{value}° {from_unit.title()} = {result:.2f}° {to_unit.title()}

Reference Points:
- Water freezes: 0°C = 32°F = 273.15K
- Water boils: 100°C = 212°F = 373.15K
- Absolute zero: -273.15°C = -459.67°F = 0K
"""
        except Exception as e:
            return f"❌ Temperature conversion error: {str(e)}"


# Export all utility tools
__all__ = [
    "PasswordGeneratorTool",
    "HashGeneratorTool",
    "ColorConverterTool",
    "UnitConverterTool",
]
