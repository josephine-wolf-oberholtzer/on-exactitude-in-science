const HtmlWebpackPlugin = require("html-webpack-plugin");
const webpack = require("webpack");
const path = require("path");

module.exports = {
	entry: "./src/index.jsx",
	module: {
		rules: [
			{
				test: /\.s?css$/,
				use: ["style-loader", "css-loader", "sass-loader"],
			},
			{
				test: /\.worker\.js$/,
				use: ["worker-loader"],
			},
			{
				test: /\.(js|jsx)$/,
				exclude: /node_modules/,
				use: ["babel-loader"],
				resolve: {
					extensions: [".js", ".jsx"],
				},
			},
			{
				test: /\.(woff|woff2|eot|ttf|otf|fnt)$/,
				use: ["file-loader"],
			},
		],
	},
	output: {
		filename: "bundle.js",
		path: path.resolve(__dirname, "dist"),
		publicPath: "/",
	},
	plugins: [
		new HtmlWebpackPlugin({
			hash: true,
			template: path.resolve(__dirname, "src", "index.html"),
		}),
		new webpack.ProvidePlugin({
			THREE: "three",
		}),
	],
};
