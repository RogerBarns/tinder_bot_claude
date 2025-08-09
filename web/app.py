"""
Quick fix for web/app.py template path issue
Run this to fix the template path in your web/app.py
"""
import os
from pathlib import Path

def fix_web_app():
    """Fix the template path in web/app.py"""
    print("🔧 Fixing web/app.py template configuration...")

    web_app_path = Path("web/app.py")

    if not web_app_path.exists():
        print("❌ web/app.py not found!")
        return False

    # Read the current content
    with open(web_app_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check current configuration
    if 'template_folder="templates"' in content:
        print("✅ Template folder already configured correctly")
        return True

    # Find the Flask app initialization line
    if 'app = Flask(__name__)' in content:
        # Replace with correct initialization
        old_line = 'app = Flask(__name__)'
        new_line = 'app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))'

        content = content.replace(old_line, new_line)

        # Make sure os is imported
        if 'import os' not in content:
            # Add import at the top after the docstring
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import') or line.startswith('from'):
                    lines.insert(i, 'import os')
                    break
            content = '\n'.join(lines)

        # Write back
        with open(web_app_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ Fixed Flask app initialization with correct template path")
        return True

    elif 'Flask(__name__, template_folder=' in content:
        # Check if it's pointing to the right place
        if 'template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")' in content:
            print("✅ Template folder path is correct")
        else:
            print("⚠️ Template folder is configured but might be pointing to wrong location")
            print("   Manual fix needed in web/app.py")
            print("   Change to: template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')")
        return True

    else:
        print("⚠️ Could not find Flask app initialization")
        print("   Please check web/app.py manually")
        return False

def create_simple_test():
    """Create a simple test file to verify everything works"""
    test_content = '''"""
Simple test to verify the dashboard loads
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_dashboard():
    """Test if dashboard loads"""
    print("Testing dashboard...")
    
    try:
        from web.app import app
        
        # Create test client
        client = app.test_client()
        
        # Test root route
        response = client.get('/')
        
        if response.status_code == 200:
            print("✅ Dashboard loads successfully!")
            
            # Check if it's HTML
            if b'<!DOCTYPE html>' in response.data:
                print("✅ Returns HTML content")
            else:
                print("⚠️ Response is not HTML")
                
            # Check for key elements
            if b'Tinder Bot Dashboard' in response.data:
                print("✅ Dashboard title found")
            else:
                print("⚠️ Dashboard title not found")
                
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard()
'''

    with open('test_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(test_content)

    print("✅ Created test_dashboard.py")

def main():
    print("=" * 60)
    print("🔧 FIXING TEMPLATE PATH ISSUES")
    print("=" * 60)

    # Fix web/app.py
    fix_web_app()

    # Create test file
    create_simple_test()

    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("=" * 60)
    print("1. Run the verification script:")
    print("   python verify_setup.py")
    print("\n2. Test the dashboard:")
    print("   python test_dashboard.py")
    print("\n3. Start the bot:")
    print("   python main.py")
    print("=" * 60)

if __name__ == "__main__":
    main()