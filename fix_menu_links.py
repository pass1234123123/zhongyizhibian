import os
with open('templates/index.html','r',encoding='utf-8') as f:
    html = f.read()

# Replace the 3 dev-in-progress menu items
html = html.replace(
    "showToast('\u529f\u80fd\u5f00\u53d1\u4e2d')",
    "showPage('pagePurchases');loadPurchases()",
    1
)
html = html.replace(
    "showToast('\u529f\u80fd\u5f00\u53d1\u4e2d')",
    "showPage('pagePoints');loadPoints()",
    1
)
html = html.replace(
    "showToast('\u529f\u80fd\u5f00\u53d1\u4e2d')",
    "showPage('pageMyUploads');loadMyUploads()",
    1
)

with open('templates/index.html','w',encoding='utf-8') as f:
    f.write(html)
print('Menu links updated')
print('Size:', os.path.getsize('templates/index.html'), 'bytes')
