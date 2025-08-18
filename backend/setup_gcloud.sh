#!/bin/bash

# Setup script for Google Cloud CLI environment
# Run this script to set up your shell environment for Google Cloud CLI

echo "🔧 Setting up Google Cloud CLI environment..."

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS setup
    if [ -f "/opt/homebrew/share/google-cloud-sdk/path.zsh.inc" ]; then
        echo "✅ Found Google Cloud SDK for macOS (Homebrew)"
        
        # Add to shell profile
        SHELL_PROFILE=""
        if [ -f "$HOME/.zshrc" ]; then
            SHELL_PROFILE="$HOME/.zshrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            SHELL_PROFILE="$HOME/.bash_profile"
        elif [ -f "$HOME/.bashrc" ]; then
            SHELL_PROFILE="$HOME/.bashrc"
        fi
        
        if [ -n "$SHELL_PROFILE" ]; then
            echo "📝 Adding Google Cloud SDK to $SHELL_PROFILE"
            
            # Check if already added
            if ! grep -q "google-cloud-sdk" "$SHELL_PROFILE"; then
                echo "" >> "$SHELL_PROFILE"
                echo "# Google Cloud SDK" >> "$SHELL_PROFILE"
                echo "source /opt/homebrew/share/google-cloud-sdk/path.zsh.inc" >> "$SHELL_PROFILE"
                echo "source /opt/homebrew/share/google-cloud-sdk/completion.zsh.inc" >> "$SHELL_PROFILE"
                echo "✅ Added to $SHELL_PROFILE"
            else
                echo "ℹ️  Google Cloud SDK already configured in $SHELL_PROFILE"
            fi
        else
            echo "⚠️  Could not find shell profile file"
        fi
        
        # Source for current session
        echo "🔄 Sourcing for current session..."
        source /opt/homebrew/share/google-cloud-sdk/path.zsh.inc
        source /opt/homebrew/share/google-cloud-sdk/completion.zsh.inc
        
    else
        echo "❌ Google Cloud SDK not found in expected location"
        echo "Please ensure it was installed via Homebrew: brew install google-cloud-sdk"
        exit 1
    fi
    
else
    echo "❌ This script is designed for macOS"
    echo "For other operating systems, please refer to:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo ""
echo "🎉 Google Cloud CLI environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Restart your terminal or run: source ~/.zshrc"
echo "2. Login to Google Cloud: gcloud auth login"
echo "3. Create a project: gcloud projects create animathic-backend"
echo "4. Set the project: gcloud config set project animathic-backend"
echo "5. Enable billing in Google Cloud Console"
echo "6. Run the deployment: ./deploy_gcp.sh"
echo ""
echo "🔗 Useful resources:"
echo "   - Google Cloud Console: https://console.cloud.google.com"
echo "   - GCP Documentation: https://cloud.google.com/docs"
echo "   - Cloud Run: https://cloud.google.com/run/docs"
echo ""
echo "✅ Setup complete! You can now use gcloud commands."
