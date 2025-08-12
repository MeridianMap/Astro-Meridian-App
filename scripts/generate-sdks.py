#!/usr/bin/env python3
"""
SDK Generation Script for Meridian Ephemeris API

This script generates client SDKs in multiple languages using OpenAPI Generator.
It processes the OpenAPI specification and creates typed client libraries.
"""

import json
import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# SDK Configurations
SDK_CONFIGS = {
    "python": {
        "generator": "python",
        "output_dir": "sdks/python",
        "package_name": "meridian_ephemeris",
        "package_version": "1.0.0",
        "config_options": {
            "packageName": "meridian_ephemeris",
            "projectName": "meridian-ephemeris-sdk",
            "packageVersion": "1.0.0",
            "packageUrl": "https://github.com/meridian-ephemeris/python-sdk",
            "packageCompany": "Meridian Ephemeris",
            "packageAuthor": "Meridian Ephemeris Team",
            "packageEmail": "support@meridianephemeris.com",
            "library": "requests",
            "generateSourceCodeOnly": "false"
        }
    },
    "typescript": {
        "generator": "typescript-axios",
        "output_dir": "sdks/typescript", 
        "package_name": "meridian-ephemeris-sdk",
        "package_version": "1.0.0",
        "config_options": {
            "npmName": "meridian-ephemeris-sdk",
            "npmVersion": "1.0.0",
            "npmRepository": "https://github.com/meridian-ephemeris/typescript-sdk.git",
            "snapshot": "false",
            "withInterfaces": "true",
            "useSingleRequestParameter": "true",
            "supportsES6": "true",
            "enumNameSuffix": "Enum",
            "modelPackage": "models",
            "apiPackage": "api"
        }
    },
    "go": {
        "generator": "go",
        "output_dir": "sdks/go",
        "package_name": "meridian-ephemeris-go",
        "package_version": "1.0.0", 
        "config_options": {
            "packageName": "meridianephemeris",
            "packageVersion": "1.0.0",
            "packageUrl": "github.com/meridian-ephemeris/go-sdk",
            "gitUserId": "meridian-ephemeris",
            "gitRepoId": "go-sdk",
            "packageCompany": "Meridian Ephemeris",
            "packageAuthor": "Meridian Ephemeris Team",
            "packageEmail": "support@meridianephemeris.com",
            "clientPackage": "client",
            "generateInterfaces": "true"
        }
    }
}

class SDKGenerator:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.openapi_spec_path = self.root_dir / "backend" / "openapi.json"
        
    def check_openapi_generator(self) -> bool:
        """Check if OpenAPI Generator is installed."""
        try:
            result = subprocess.run(
                ["openapi-generator-cli", "version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ OpenAPI Generator found: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
            
        print("❌ OpenAPI Generator CLI not found")
        print("Install with: npm install -g @openapitools/openapi-generator-cli")
        print("Or download from: https://openapi-generator.tech/docs/installation")
        return False
    
    def generate_openapi_spec(self) -> bool:
        """Generate the OpenAPI specification from FastAPI app."""
        print("📊 Generating OpenAPI specification...")
        
        try:
            # Change to backend directory and generate spec
            backend_dir = self.root_dir / "backend"
            os.chdir(backend_dir)
            
            result = subprocess.run([
                sys.executable, "-c",
                "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))"
            ], capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "."})
            
            if result.returncode != 0:
                print(f"❌ Failed to generate OpenAPI spec: {result.stderr}")
                return False
                
            # Write the spec to file
            with open(self.openapi_spec_path, "w") as f:
                f.write(result.stdout)
                
            print(f"✅ OpenAPI spec generated: {self.openapi_spec_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating OpenAPI spec: {e}")
            return False
        finally:
            os.chdir(self.root_dir)
    
    def enhance_openapi_spec(self) -> Dict[str, Any]:
        """Enhance OpenAPI spec with additional metadata for better SDK generation."""
        print("🔧 Enhancing OpenAPI specification...")
        
        with open(self.openapi_spec_path, "r") as f:
            spec = json.load(f)
        
        # Add server information
        spec["servers"] = [
            {
                "url": "https://api.meridianephemeris.com",
                "description": "Production server"
            },
            {
                "url": "http://localhost:8000", 
                "description": "Development server"
            }
        ]
        
        # Enhance info section
        spec["info"]["title"] = "Meridian Ephemeris API"
        spec["info"]["description"] = (
            "Professional astrological calculations using the Swiss Ephemeris. "
            "Calculate precise natal charts, planetary positions, and house systems "
            "with support for multiple coordinate and datetime formats."
        )
        
        # Add tags for better organization
        spec["tags"] = [
            {
                "name": "health",
                "description": "Health check and service status endpoints"
            },
            {
                "name": "ephemeris", 
                "description": "Astrological calculation endpoints"
            }
        ]
        
        # Add examples to schemas
        if "components" in spec and "schemas" in spec["components"]:
            self._add_schema_examples(spec["components"]["schemas"])
        
        return spec
    
    def _add_schema_examples(self, schemas: Dict[str, Any]) -> None:
        """Add examples to schema definitions."""
        examples = {
            "NatalChartRequest": {
                "subject": {
                    "name": "John Doe",
                    "datetime": {"iso_string": "1990-06-15T14:30:00"},
                    "latitude": {"decimal": 40.7128},
                    "longitude": {"decimal": -74.0060},
                    "timezone": {"name": "America/New_York"}
                },
                "settings": {
                    "house_system": "placidus"
                }
            },
            "SubjectRequest": {
                "name": "John Doe",
                "datetime": {"iso_string": "1990-06-15T14:30:00"},
                "latitude": {"decimal": 40.7128},
                "longitude": {"decimal": -74.0060},
                "timezone": {"name": "America/New_York"}
            },
            "CoordinateInput": {
                "decimal": 40.7128
            },
            "DateTimeInput": {
                "iso_string": "1990-06-15T14:30:00"
            },
            "TimezoneInput": {
                "name": "America/New_York"
            }
        }
        
        for schema_name, example in examples.items():
            if schema_name in schemas:
                schemas[schema_name]["example"] = example
    
    def generate_sdk(self, language: str) -> bool:
        """Generate SDK for specified language."""
        if language not in SDK_CONFIGS:
            print(f"❌ Unsupported language: {language}")
            return False
        
        config = SDK_CONFIGS[language]
        print(f"🔨 Generating {language} SDK...")
        
        # Create output directory
        output_dir = self.root_dir / config["output_dir"]
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create config options string
        config_opts = ",".join([
            f"{key}={value}" for key, value in config["config_options"].items()
        ])
        
        # Generate SDK
        cmd = [
            "openapi-generator-cli", "generate",
            "-i", str(self.openapi_spec_path),
            "-g", config["generator"],
            "-o", str(output_dir),
            "--additional-properties", config_opts,
            "--skip-validate-spec"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {language} SDK generated successfully")
                self._post_process_sdk(language, output_dir)
                return True
            else:
                print(f"❌ Failed to generate {language} SDK:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error generating {language} SDK: {e}")
            return False
    
    def _post_process_sdk(self, language: str, output_dir: Path) -> None:
        """Post-process generated SDK."""
        print(f"🔧 Post-processing {language} SDK...")
        
        if language == "python":
            self._post_process_python_sdk(output_dir)
        elif language == "typescript":
            self._post_process_typescript_sdk(output_dir)
        elif language == "go":
            self._post_process_go_sdk(output_dir)
    
    def _post_process_python_sdk(self, output_dir: Path) -> None:
        """Post-process Python SDK."""
        # Create a convenience wrapper
        wrapper_content = '''"""
Meridian Ephemeris SDK - Convenience Wrapper

This module provides a simplified interface to the Meridian Ephemeris API.
"""

from .api_client import ApiClient
from .configuration import Configuration
from .apis import EphemerisApi
from .models import *

__version__ = "1.0.0"

class MeridianEphemeris:
    """Simplified client for Meridian Ephemeris API."""
    
    def __init__(self, base_url: str = "https://api.meridianephemeris.com"):
        """Initialize the client."""
        config = Configuration(host=base_url)
        self.api_client = ApiClient(config)
        self.ephemeris = EphemerisApi(self.api_client)
    
    def calculate_natal_chart(self, subject_data: dict, settings: dict = None) -> dict:
        """Calculate a natal chart."""
        from .models import NatalChartRequest, SubjectRequest
        
        # Convert dict to proper models
        subject = SubjectRequest(**subject_data)
        request = NatalChartRequest(subject=subject, settings=settings or {})
        
        # Make API call
        response = self.ephemeris.natal_chart_ephemeris_natal_post(request)
        return response.to_dict()
    
    def health_check(self) -> dict:
        """Check API health."""
        response = self.ephemeris.health_check_ephemeris_health_get()
        return response.to_dict()
'''
        
        with open(output_dir / "meridian_ephemeris" / "__init__.py", "w") as f:
            f.write(wrapper_content)
    
    def _post_process_typescript_sdk(self, output_dir: Path) -> None:
        """Post-process TypeScript SDK."""
        # Create index.ts file for better exports
        index_content = '''/**
 * Meridian Ephemeris SDK for TypeScript/JavaScript
 * 
 * Professional astrological calculations using the Swiss Ephemeris.
 */

export * from './api';
export * from './models';
export * from './configuration';

import { EphemerisApi, Configuration } from './api';

/**
 * Simplified client for Meridian Ephemeris API
 */
export class MeridianEphemeris {
    private api: EphemerisApi;
    
    constructor(baseURL: string = 'https://api.meridianephemeris.com') {
        const config = new Configuration({
            basePath: baseURL
        });
        this.api = new EphemerisApi(config);
    }
    
    /**
     * Calculate a natal chart
     */
    async calculateNatalChart(subjectData: any, settings?: any): Promise<any> {
        const request = {
            subject: subjectData,
            settings: settings || {}
        };
        
        const response = await this.api.natalChartEphemerisNatalPost(request);
        return response.data;
    }
    
    /**
     * Check API health
     */
    async healthCheck(): Promise<any> {
        const response = await this.api.healthCheckEphemerisHealthGet();
        return response.data;
    }
}
'''
        
        with open(output_dir / "index.ts", "w") as f:
            f.write(index_content)
    
    def _post_process_go_sdk(self, output_dir: Path) -> None:
        """Post-process Go SDK."""
        # Create a convenience client wrapper
        client_content = '''package meridianephemeris

import (
    "context"
    "net/http"
)

// MeridianEphemeris provides a simplified interface to the API
type MeridianEphemeris struct {
    client *APIClient
}

// NewClient creates a new Meridian Ephemeris client
func NewClient(baseURL string) *MeridianEphemeris {
    if baseURL == "" {
        baseURL = "https://api.meridianephemeris.com"
    }
    
    config := NewConfiguration()
    config.Servers = ServerConfigurations{
        {URL: baseURL},
    }
    
    return &MeridianEphemeris{
        client: NewAPIClient(config),
    }
}

// CalculateNatalChart calculates a natal chart
func (m *MeridianEphemeris) CalculateNatalChart(ctx context.Context, request NatalChartRequest) (*NatalChartResponse, *http.Response, error) {
    return m.client.EphemerisApi.NatalChartEphemerisNatalPost(ctx).NatalChartRequest(request).Execute()
}

// HealthCheck checks API health  
func (m *MeridianEphemeris) HealthCheck(ctx context.Context) (*HealthResponse, *http.Response, error) {
    return m.client.EphemerisApi.HealthCheckEphemerisHealthGet(ctx).Execute()
}
'''
        
        with open(output_dir / "client.go", "w") as f:
            f.write(client_content)
    
    def run(self, languages: list = None) -> bool:
        """Run the complete SDK generation process."""
        print("🚀 Starting SDK generation...")
        
        # Check prerequisites
        if not self.check_openapi_generator():
            return False
        
        # Generate OpenAPI spec
        if not self.generate_openapi_spec():
            return False
        
        # Enhance the spec
        enhanced_spec = self.enhance_openapi_spec()
        
        # Write enhanced spec
        with open(self.openapi_spec_path, "w") as f:
            json.dump(enhanced_spec, f, indent=2)
        
        # Generate SDKs
        languages = languages or list(SDK_CONFIGS.keys())
        success = True
        
        for language in languages:
            if not self.generate_sdk(language):
                success = False
        
        if success:
            print("\n✅ All SDKs generated successfully!")
            self._print_usage_instructions()
        else:
            print("\n❌ Some SDK generation failed")
        
        return success
    
    def _print_usage_instructions(self) -> None:
        """Print usage instructions for generated SDKs."""
        print("\n📦 Generated SDKs:")
        print("├── Python SDK: sdks/python/")
        print("│   └── Install: pip install ./sdks/python")
        print("├── TypeScript SDK: sdks/typescript/") 
        print("│   └── Install: npm install ./sdks/typescript")
        print("└── Go SDK: sdks/go/")
        print("    └── Import: github.com/meridian-ephemeris/go-sdk")
        
        print("\n📚 Example usage:")
        print("\n# Python")
        print("from meridian_ephemeris import MeridianEphemeris")
        print("client = MeridianEphemeris()")
        print("chart = client.calculate_natal_chart({...})")
        
        print("\n// TypeScript")
        print("import { MeridianEphemeris } from 'meridian-ephemeris-sdk';")
        print("const client = new MeridianEphemeris();")
        print("const chart = await client.calculateNatalChart({...});")
        
        print("\n// Go")
        print("import \"github.com/meridian-ephemeris/go-sdk\"")
        print("client := meridianephemeris.NewClient(\"\")")
        print("chart, _, err := client.CalculateNatalChart(ctx, request)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Meridian Ephemeris SDKs")
    parser.add_argument("--languages", nargs="+", choices=list(SDK_CONFIGS.keys()),
                       help="Languages to generate SDKs for")
    parser.add_argument("--check", action="store_true", 
                       help="Only check prerequisites")
    
    args = parser.parse_args()
    
    generator = SDKGenerator()
    
    if args.check:
        generator.check_openapi_generator()
    else:
        generator.run(args.languages)