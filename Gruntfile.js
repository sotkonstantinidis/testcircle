module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    // Sass: Compiles .scss files and saves them as .css
    sass: {
      options: {
        includePaths: [
          'bower_components/compass-mixins/lib',
          'bower_components/foundation/scss'],
        imagePath: '/assets/img'
      },
      dev: {
        options: {
          outputStyle: 'nested'
        },
        files: {
          'static/css/app.css': 'src/scss/app.scss'
        }
      },
      deploy: {
        options: {
          outputStyle: 'compressed'
        },
        files: {
          'static/css/app.css': 'src/scss/app.scss'
        }
      }
    },

    // Assemble: Compiles .hbs files and saves them as .html
    assemble: {
      options: {
        layoutdir: 'src/layout/',
        layout: 'default.hbs',
        flatten: true
      },
      pages: {
        options:{
          partials: ['src/partial/**/*.hbs']
        },
        files: {
          'static/': ['src/page/*.hbs']
        }
      }
    },

    // Imagemin: Minifies and copies images
    imagemin: {
      main: {
        files: [{
          expand: true,
          cwd: 'src/assets/img',
          src: ['**/*.{png,jpg,gif}'],
          dest: 'static/assets/img'
        }]
      }
    },

    // Copy: copies files (libraries and single files, e.g. fonts)
    copy: {
      main: {
        files: [{
          'static/js/modernizr.js': 'bower_components/modernizr/modernizr.js',
          'static/js/jquery.min.js': 'bower_components/jquery/dist/jquery.min.js',
          'static/js/jquery.min.map': 'bower_components/jquery/dist/jquery.min.map',
          'static/js/foundation.min.js': 'bower_components/foundation/js/foundation.min.js',
          'static/js/dropzone.min.js': 'bower_components/dropzone/downloads/dropzone.min.js',
          'static/js/app.js': 'src/js/app.js'
        }]
      },
      assets: {
        files: [{
          expand: true,
          cwd: 'src/assets/files',
          src: ['**/*'],
          dest: 'static/assets/files'
        },{
          expand: true,
          cwd: 'src/assets/fonts',
          src: ['**/*'],
          dest: 'static/assets/fonts'
        },{
          // Copy svg
          expand: true,
          cwd: 'src/assets/img',
          src: ['*.svg'],
          dest: 'static/assets/img'
        }]
      }
    },

    // Watch: check for changes and reload web browser
    watch: {
      sass: {
        files: 'src/scss/**/*.scss',
        tasks: ['sass'],
        options: {
          livereload: true,
        }
      },
      assets: {
        files: 'src/assets/**/*',
        tasks: ['copy', 'imagemin'],
        options: {
          livereload: true,
        }
      },
      js: {
        files: 'src/js/**/*.js',
        tasks: ['copy'],
        options: {
          livereload: true,
        }
      },
      html: {
        files: ['src/**/*.hbs', 'src/embed/**/*'],
        tasks: ['assemble'],
        options: {
          livereload: true,
        }
      }
    },

    // Connect: Grunt server
    connect: {
      server: {
        options: {
          hostname: '0.0.0.0',
          port: 8000,
          livereload: true,
          open: true,
          base: 'static'
        }
      }
    }
  });

  grunt.loadNpmTasks('assemble');
  grunt.loadNpmTasks('grunt-sass');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.loadNpmTasks('grunt-contrib-imagemin');

  /**
   * Available commands:
   * grunt                : Build (uncompressed) and run the server
   * grunt build          : Build (uncompressed)
   * grunt build:deploy   : Build (compressed)
   * grunt server         : Run the server
   */
  grunt.registerTask('build', function(arg) {
    // Default mode is 'dev'
    var mode = (arg && arg === 'deploy') ? 'deploy' : 'dev';
    grunt.task.run(['sass:' + mode, 'imagemin', 'copy', 'assemble']);
  });
  grunt.registerTask('server', ['connect:server', 'watch']);
  grunt.registerTask('default', ['build', 'server']);
}
