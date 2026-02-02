import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# Check available fonts
fonts = [f.name for f in fm.fontManager.ttflist if 'Devanagari' in f.name or 'Noto' in f.name]
print("Available Devanagari fonts:", fonts)

# Test Hindi rendering
fig, ax = plt.subplots()
ax.text(0.5, 0.5, 'हिन्दी परीक्षण', fontsize=20)
plt.show()