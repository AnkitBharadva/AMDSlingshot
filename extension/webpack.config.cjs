const path = require('path');

module.exports = {
  entry: {
    'content-script': './content/content-script.ts',
    'popup': './ui/popup.js',
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'dist'),
  },
  optimization: {
    minimize: false, // Keep code readable for debugging
  },
};
