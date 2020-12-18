var pluginsConfig = {
      Crop: {
        controlsCss: {
          width: '15px',
          height: '15px',
          background: 'white',
          border: '1px solid black'
        },
        controlsTouchCss: {
          width: '25px',
          height: '25px',
          background: 'white',
          border: '2px solid black'
        }
      },
      Rotate: {
        controlsCss: {
          width: '15px',
          height: '15px',
          background: 'white',
          border: '1px solid black'
        },
        controlsTouchCss: {
          width: '25px',
          height: '25px',
          background: 'white',
          border: '2px solid black'
        }
      },
      Resize: {
        controlsCss: {
          width: '15px',
          height: '15px',
          background: 'white',
          border: '1px solid black'
        },
        controlsTouchCss: {
          width: '25px',
          height: '25px',
          background: 'white',
          border: '2px solid black'
        }
      }
    };
      
var pluginsConfig = {
  Rotate: {
    controlsCss: {
      width: '15px',
      height: '15px',
      background: 'white',
      border: '1px solid black'
    },
    controlsTouchCss: {
      width: '25px',
      height: '25px',
      background: 'white',
      border: '2px solid black'
    }
  },
  Resize: {
    controlsCss: {
      width: '15px',
      height: '15px',
      background: 'white',
      border: '1px solid black'
    },
    controlsTouchCss: {
      width: '25px',
      height: '25px',
      background: 'white',
      border: '2px solid black'
    }
  },
  Crop: {
    controlsCss: {
      width: '15px',
      height: '15px',
      background: 'white',
      border: '1px solid black'
    },
    controlsTouchCss: {
      width: '25px',
      height: '25px',
      background: 'white',
      border: '2px solid black'
    }
  },
  Toolbar: {
    toolbarSize: 85,
    toolbarSizeTouch: 43,
    tooltipEnabled: true,
    tooltipCss: {
      color: 'white',
      background: 'black'
    }
  },
  Delete: {
    fullRemove: true
  },
  Save: {
    upload: true,
    uploadFunction: function (imageId, imageData, callback) {
      var imager = this;
      console.log('uploading ' + imageId);
      var data = imageData.replace(/^data:image\/(png|jpg|jpeg);base64,/, '');
      var dataJson = '{ "imageId": "' + imageId + '", "imageData" : "' + data + '" }';
      $.ajax({
        url: 'http://www.vamostrabalharjuntos.com.br/projetos/save',
        dataType: 'json',
        data: dataJson,
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        success: function(imageUrl) {
          callback(imageUrl); // assuming that server returns an `imageUrl` as a response
          console.log('uploading success: ' + imageUrl);
        },
        error: function (xhr, status, error) {
          console.log(error);
        }
      });
    }
  }
};

var options = {
  plugins: ['Rotate', 'Crop', 'Resize', 'Toolbar', 'Save', 'Delete', 'Undo'],
  editModeCss: {
  },
  pluginsConfig: pluginsConfig,
  quality: {
    sizes: [
      { label: 'Original', scale: 1, quality: 1, percentage: 100 },
      { label: 'Large', scale: 0.5, quality: 0.5, percentage: 50 },
      { label: 'Medium', scale: 0.2, quality: 0.2, percentage: 20 },
      { label: 'Small', scale: 0.05, quality: 0.05, percentage: 5 }
    ],
    allowCustomSetting: true
  },

  contentConfig: {
    saveImageData: function (imageId, imageData) {
      try {
        console.log('Save button clicked! ImageId:', imageId);
        console.log('ImageData argument here is the image encoded in base64 string. ' +
          'This function gets called anytime user clicks on `save` button. ' +
          'If one wants to disable edit after saving, check the `standalone-remote-upload.html` ' +
          'example file which shows how to upload image on the server ' +
          'and display it in place of ImagerJs after that.');
        localStorage.setItem('image_' + imageId, imageData);
      } catch (err) {
        console.error(err);
      }
    }
  }
};