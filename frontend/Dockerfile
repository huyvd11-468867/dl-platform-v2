FROM nginx:alpine

# Copy HTML file to nginx
COPY index.html /usr/share/nginx/html/

# Ensure static files are world-readable so nginx worker (non-root) can serve them
RUN chmod 644 /usr/share/nginx/html/index.html || true

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
