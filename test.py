from dotenv import load_dotenv
import os

print("🔍 Testing your setup...\n")
print("Current directory:", os.getcwd())
print("Files in directory:", os.listdir('.'))

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if api_key:
    print(f"\n✅ API Key found: {api_key[:10]}...")
    print("✅ Setup looks good! You're ready to go!")
else:
    print("\n❌ API Key not found")
    print("\n📝 Please follow these steps:")
    print("1. Go to https://aistudio.google.com/app/apikey")
    print("2. Get your free API key")
    print("3. Create a .env file in this folder")
    print("4. Add this line: GEMINI_API_KEY=your_api_key_here")
    
# Check if .env file exists
print("\n" + "="*50)
if os.path.exists('.env'):
    print("✅ .env file exists")
    with open('.env', 'r') as f:
        content = f.read()
        if content.strip():
            print("✅ .env file has content")
        else:
            print("⚠️ .env file is empty - please add your API key")
else:
    print("❌ .env file not found - you need to create it!")
    
print("="*50)