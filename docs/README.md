# BitMshauri Bot - GitHub Pages Documentation

This directory contains the complete documentation website for the BitMshauri bot, deployed via GitHub Pages.

## 📁 File Structure

```
docs/
├── index.html              # Main landing page
├── user-guide.html         # Complete user guide
├── developer-guide.html    # Developer documentation
├── api-reference.html      # API documentation
├── styles.css              # Main stylesheet
├── script.js               # Interactive JavaScript
└── README.md               # This file
```

## 🚀 GitHub Pages Deployment

This documentation site is automatically deployed to GitHub Pages when changes are pushed to the main branch.

### Deployment Process

1. **Automatic Deployment**: The GitHub Actions workflow (`.github/workflows/deploy.yml`) automatically builds and deploys the site
2. **Source Branch**: `main`
3. **Deploy Branch**: `gh-pages`
4. **Site URL**: `https://mwanga-lab.github.io/bitmshauri-bot/`

### Manual Deployment

If you need to deploy manually:

```bash
# Install dependencies
npm install -g http-server

# Test locally
cd docs
http-server -p 8000

# Deploy using GitHub Actions
git add .
git commit -m "Update documentation"
git push origin main
```

## 🎨 Design Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional design with Bitcoin-themed colors
- **Interactive Elements**: Smooth animations, hover effects, and dynamic content
- **Accessibility**: Proper semantic HTML and ARIA labels
- **Performance**: Optimized CSS and JavaScript for fast loading

## 📱 Pages Overview

### Landing Page (`index.html`)
- Hero section with bot preview
- Feature showcase
- Getting started guide
- Documentation links
- Contact information

### User Guide (`user-guide.html`)
- Complete bot usage instructions
- Command reference
- Feature explanations
- Troubleshooting guide
- Multi-language support

### Developer Guide (`developer-guide.html`)
- Architecture overview
- Setup instructions
- Project structure
- Database schema
- API integrations
- Testing guidelines
- Deployment options
- Contributing guidelines

### API Reference (`api-reference.html`)
- API endpoints documentation
- Request/response examples
- Authentication details
- Rate limiting information
- Code examples in multiple languages

## 🛠️ Customization

### Colors
The site uses a Bitcoin-themed color palette:
- Primary: `#f7931a` (Bitcoin Orange)
- Secondary: `#ff9500` (Orange)
- Text: `#1f2937` (Dark Gray)
- Background: `#f8fafc` (Light Gray)

### Fonts
- Primary: Inter (Google Fonts)
- Code: Monaco/Menlo (System fonts)

### Icons
- Font Awesome 6.0.0 for all icons

## 📊 Analytics

The site includes:
- Google Analytics (if configured)
- Performance monitoring
- User interaction tracking

## 🔧 Maintenance

### Regular Updates
- Keep documentation in sync with bot features
- Update API documentation when endpoints change
- Review and update links regularly
- Test responsive design on different devices

### Content Guidelines
- Use clear, concise language
- Include code examples where appropriate
- Maintain consistent formatting
- Update screenshots when UI changes

## 🐛 Troubleshooting

### Common Issues

1. **Site not updating**: Check GitHub Actions workflow status
2. **Styling issues**: Clear browser cache and check CSS file
3. **Broken links**: Verify all internal and external links
4. **Mobile display**: Test on actual mobile devices

### Support

For documentation issues:
- Create an issue in the main repository
- Contact: mwanga02717@gmail.com
- Check GitHub Actions logs for deployment errors

## 📄 License

This documentation is part of the BitMshauri bot project and is licensed under the MIT License.

---

**BitMshauri – Empowering East Africa with Bitcoin Education** 🚀
