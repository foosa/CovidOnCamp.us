/*
 * Main Javascript file for sarscov2_gatech_community_survey.
 *
 * This file bundles all of your javascript together using webpack.
 */

// JavaScript modules
import $ from 'jquery';

require('@fortawesome/fontawesome-free');
require('jquery');
require('popper.js');
require('bootstrap');

require.context(
  '../img', // context folder
  true, // include subdirectories
  /.*/, // RegExp
);

// Your own code
require('./plugins.js');
require('./script.js');

