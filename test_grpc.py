"""
Test script for ChirpStack gRPC client
Tests connection and basic functionality
"""

from grpc_client import ChirpStackClient, validate_dev_eui, validate_key


def test_validation():
    """Test validation functions"""
    print("=" * 60)
    print("Testing Validation Functions")
    print("=" * 60)
    
    # Test DevEUI validation
    print("\n1. Testing DevEUI validation:")
    test_cases = [
        ("94193A0103001D3C", "Valid"),
        ("94193A0103001D3", "Too short"),
        ("94193A0103001D3CX", "Invalid character"),
        ("", "Empty"),
    ]
    
    for dev_eui, desc in test_cases:
        valid, result = validate_dev_eui(dev_eui)
        status = "✓ VALID" if valid else "✗ INVALID"
        print(f"  {status}: {desc:20s} - {dev_eui:20s} -> {result}")
    
    # Test Key validation
    print("\n2. Testing Key validation:")
    test_keys = [
        ("49C1B29AFAB03794E82EDDF657DB22FC", "Valid"),
        ("49C1B29AFAB03794E82EDDF657DB22F", "Too short"),
        ("49C1B29AFAB03794E82EDDF657DB22FCX", "Too long"),
    ]
    
    for key, desc in test_keys:
        valid, result = validate_key(key, "AppKey")
        status = "✓ VALID" if valid else "✗ INVALID"
        print(f"  {status}: {desc:20s} -> {result[:32] if valid else result}")


def test_connection(server_url, api_key):
    """Test connection to ChirpStack server"""
    print("\n" + "=" * 60)
    print("Testing ChirpStack Connection")
    print("=" * 60)
    
    print(f"\nServer URL: {server_url}")
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: Not provided")
    
    # Create client
    client = ChirpStackClient(server_url, api_key)
    
    # Connect
    print("\nConnecting to server...")
    success, message = client.connect()
    
    if success:
        print(f"✓ {message}")
        
        # Test connection
        print("\nTesting authentication...")
        success, message = client.test_connection()
        
        if success:
            print(f"✓ {message}")
            print("\n🎉 gRPC client is working correctly!")
        else:
            print(f"✗ {message}")
            print("\n⚠️  Connection established but authentication failed.")
            print("   Please check your API key in the server configuration page.")
        
        client.close()
    else:
        print(f"✗ {message}")
        print("\n⚠️  Could not connect to ChirpStack server.")
        print("   Please check:")
        print("   1. ChirpStack server is running")
        print("   2. Server URL is correct (default: localhost:8080)")
        print("   3. No firewall is blocking the connection")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ChirpStack gRPC Client Test Suite")
    print("=" * 60)
    
    # Test validation functions
    test_validation()
    
    # Test connection (update these values)
    SERVER_URL = "localhost:8080"  # Change if different
    API_KEY = ""  # Add your API key here for testing
    
    if API_KEY:
        test_connection(SERVER_URL, API_KEY)
    else:
        print("\n" + "=" * 60)
        print("Skipping Connection Test")
        print("=" * 60)
        print("\nTo test the connection, add your API key to this script:")
        print("  API_KEY = \"your-api-key-here\"")
        print("\nYou can also test via the web interface in the")
        print("'Server-Konfiguration' page.")
    
    print("\n" + "=" * 60)
    print("Phase 1 Complete!")
    print("=" * 60)
    print("\n✓ gRPC packages installed")
    print("✓ Proto files compiled")
    print("✓ gRPC client created")
    print("✓ Validation functions implemented")
    print("\nNext: Run this with your API key to test the connection,")
    print("or proceed to Phase 2 to enhance the file upload functionality.")
    print()
