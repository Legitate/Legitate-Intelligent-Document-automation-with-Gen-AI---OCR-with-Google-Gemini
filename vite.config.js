export default {
  server: {
    proxy: {
      '/upload': 'http://localhost:5000',
    },
  },
};
