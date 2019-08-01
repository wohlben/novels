const path = require('path');
const glob = require('glob');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');


module.exports = {
  mode: 'development',
  optimization: {
    minimizer: [
      new UglifyJsPlugin({
        cache: true,
        parallel: true,
        sourceMap: false
      }),
      new OptimizeCSSAssetsPlugin({})
    ]
  },
  entry: {
    './js/app.js': ['./js/app.js'].concat(glob.sync('./vendor/**/*.js')),
    //'./js/base.js': ['./js/base.js'],
    //'./js/chapter.js': ['./js/chapter.js'],
    './css/app': ['./scss/app.scss'],
    './css/chapter': ['./scss/chapter.scss'],
    //'./chapter.js': ['./js/chapter.js'],
    //'./profile.js': ['./js/profile.js']
  },
  output: {
    filename: '[name]',
    path: path.resolve(__dirname, '../static/dist')
  },
  module: {
    rules: [{
        test: /\.(s*)css$/,
        exclude: /node_modules/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
          },
          {
            loader: 'css-loader'
          },
          {
            loader: 'sass-loader'
          }
        ]
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader'
        }
      }
    ]
  },
  plugins: [
    new BundleTracker({
      filename: './webpack-stats.json'
    }),
    new MiniCssExtractPlugin({
      filename: './[name].css'
    }),
    new CopyWebpackPlugin([{
      from: 'node_modules/bootswatch/dist',
      to: './css/bootswatch/'
    }, {
      from: 'node_modules/font-awesome',
      to: './font-awesome/'
    },{
      from: 'node_modules/awesomplete/awesomplete.min.js',
      to: './js/awesomplete.min.js'
    }, {
      from: 'node_modules/awesomplete/awesomplete.css',
      to: './css/awesomplete.css'
    }, {
      from: 'node_modules/paginationjs/dist/pagination.css',
      to: './css/pagination.css'
    }, {
      from: 'node_modules/jquery/dist/jquery.min.js',
      to: './js/jquery.min.js'
    }, {
      from: 'node_modules/paginationjs/dist/pagination.min.js',
      to: './js/pagination.min.js'
    }, {
      from: 'node_modules/js-cookie/src/js.cookie.js',
      to: './js/js.cookie.js'
    }, {
      from: 'node_modules/bootstrap/dist/js/bootstrap.bundle.min.js',
      to: './js/bootstrap.bundle.min.js'
    }, {
      from: 'node_modules/intercooler/dist/intercooler.js',
      to: './js/intercooler.js'
    }
    ]),
  ]
}