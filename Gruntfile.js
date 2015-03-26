module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    // Sass: Compiles .scss files and saves them as .css
    sass: {
      options: {
        includePaths: ['bower_components/foundation/scss'],
      },
      dev: {
        options: {
          outputStyle: 'nested',
          imagePath: '/assets/img'
        },
        files: {
          'static/css/app.css': 'src/scss/app.scss'
        }
      },
      deploy: {
        options: {
          outputStyle: 'compressed',
          imagePath: 'static/assets/img'
        },
        files: {
          'static/css/app.css': 'src/scss/app.scss'
        }
      }
    },

    // CSS Autorpefix https://github.com/postcss/autoprefixer
    postcss: {
      options: {
        map: true,
        processors: [
          require('autoprefixer-core')({browsers: 'last 1 version'}).postcss,
          require('csswring').postcss
        ]
      },
      dist: {
        src: 'static/css/app.css'
      }
    },

    // Assemble: Compiles .hbs files and saves them as .html
    assemble: {
      options: {
        layoutdir: 'src/layout/',
        layout: 'default.hbs',
        data: 'src/data/*.json',
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
      },
    },

    // SVG Store for vector icons
    svgstore: {
      options: {
        prefix : 'icon-', // This will prefix each ID
        cleanup: true,
        svg: { // will add and overide the the default xmlns="http://www.w3.org/2000/svg" attribute to the resulting SVG
          style: "display: none;"
        }
      },
      dist: {
        files: {
          'src/partial/svg_icons.hbs': ['src/assets/icons/*.svg']
        }
      },
    },

    // Copy: copies files (libraries and single files, e.g. fonts)
    copy: {
      main: {
        files: [{
          'static/js/modernizr.js': 'bower_components/modernizr/modernizr.js',
          'static/js/jquery.min.js': 'bower_components/jquery/dist/jquery.min.js',
          'static/js/jquery.min.map': 'bower_components/jquery/dist/jquery.min.map',
          'static/js/dropzone.min.js': 'bower_components/dropzone/downloads/dropzone.min.js',
          'static/js/app.js': 'src/js/app.js',
          'static/js/wocat.magellan.js': 'src/js/wocat.magellan.js',
          'static/js/wizard.js': 'src/js/wizard.js'
        },{
          expand: true,
          cwd: 'bower_components/foundation/js/foundation/',
          src: ['**/*'],
          dest: 'static/js/foundation/'
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
      },
      data: {
        files: 'src/data/*.json',
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
  grunt.loadNpmTasks('grunt-postcss');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.loadNpmTasks('grunt-contrib-imagemin');
  grunt.loadNpmTasks('grunt-svgstore');

  /**
   * Available commands:
   * IMPORTANT: Update the documentation if you edit or add commands.
   * grunt                : Build (uncompressed) and run the server
   * grunt build          : Build (uncompressed)
   * grunt build:deploy   : Build (compressed)
   * grunt server         : Run the server
   */
  grunt.registerTask('build', function(arg) {
    // Default mode is 'dev'
    var mode = (arg && arg === 'deploy') ? 'deploy' : 'dev';
    grunt.task.run(['sass:' + mode, 'svgstore', 'imagemin', 'copy', 'assemble']);
  });
  grunt.registerTask('server', ['connect:server', 'watch']);
  grunt.registerTask('default', ['build', 'server']);
}
