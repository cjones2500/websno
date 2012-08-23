var PI2 = Math.PI * 2;

var websnoed = (function() {
  var wsed = {
    container: null,
    camera: null,
    scene: null,
    renderer: null,
    ray: null,
    projector: null,
    mouse3D: null,

    isMouseDown: false,
    onMouseDownPosition:  null,
    onMouseDownPhi: 60,
    onMouseDownTheta: 45,

    radius: 375,
    theta: 45,
    phi: 60,

    NPMTS: pmtpos.x.length,
    pmts: [],
    prevHits: new Array(),

    particleSurfaceProgram: function(context) {
      context.beginPath();
      context.arc(0, 0, 1, 0, PI2, true);
      context.closePath();
      context.fill();
    },
  };

  wsed.hitMaterial = new THREE.ParticleCanvasMaterial({
    color: 0xff0000,
    program: wsed.particleSurfaceProgram
  });

  wsed.unhitMaterial = new THREE.ParticleCanvasMaterial({
    color: 0x555555,
    program: wsed.particleSurfaceProgram
  });

  wsed.init = function() {
    // div elements (plots, etc.)
    wsed.container = document.createElement('div');
    document.body.appendChild(wsed.container);

    var event_metadata = document.createElement('div');
    event_metadata.style.position = 'absolute';
    event_metadata.id = 'event-meta';
    event_metadata.style.top = '10px';
    event_metadata.style.width = '300px';
    event_metadata.style.height = '105px';
    event_metadata.style.color = 'white';
    event_metadata.style.background = '0xaaa';
    event_metadata.style.border = 'solid 1px 0x55555';
    event_metadata.innerHTML = '<div style="border:solid 1px 0x55555"><div id="meta-nhit"></div><div id="meta-gtid"></div></div>';
    wsed.container.appendChild(event_metadata);

    var crates = document.createElement('div');
    crates.style.position = 'absolute';
    crates.id = 'crates';
    crates.style.top = '10px';
    crates.style.left = String(window.innerWidth - 300) + 'px';
    crates.style.width = '300px';
    crates.style.height = '105px';
    crates.style.color = 'white';
    crates.style.background = '0xaaa';
    crates.style.border = 'solid 1px 0x55555';
    crates.innerHTML = '<div id="crates"></div>';
    wsed.container.appendChild(crates);

    var charge_plot = document.createElement('div');
    charge_plot.style.position = 'absolute';
    charge_plot.id = 'plot-charge';
    charge_plot.style.top = '110px';
    charge_plot.style.width = '300px';
    charge_plot.style.height = '175px';
    charge_plot.style.color = 'white';
    charge_plot.style.background = 'black';
    charge_plot.style.textAlign = 'center';
    wsed.container.appendChild(charge_plot);

    var time_plot = document.createElement('div');
    time_plot.style.position = 'absolute';
    time_plot.id = 'plot-time';
    time_plot.style.top = '285px';
    time_plot.style.width = '300px';
    time_plot.style.height = '175px';
    time_plot.style.color = 'white';
    time_plot.style.background = 'black';
    time_plot.style.textAlign = 'center';
    wsed.container.appendChild(time_plot);

    // crate view
    var html = '<table style="font-size:4pt"><tr>';
    for (var icrate=0; icrate<19; icrate++) {
      html += '<td><table cellspacing="1px" cellpadding="1px">';
      for (var ichan=0; ichan<32; ichan++) {
        html += '<tr>'
        for (var icard=0; icard<16; icard++) {
          html += '<td style="height:1px;width:1px;background:#555555" id="channel-' + icrate + '_' + icard + '_' + ichan + '"></td>';
        }
        html += '</tr>';
      }
      html += '</table></td>';
      if ((icrate+1) % 4 == 0) {
        html += '</tr><tr>';
      }
    }
    html += '</tr></table>';

    $("#crates").append(html);

    // scene
    wsed.scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 10000);
    camera.position.y = wsed.radius;
    camera.rotation.y = -Math.PI/2;
    camera.updateMatrix();
    camera.lookAt(wsed.scene.position);

    wsed.camera = camera;
    wsed.scene.add(wsed.camera);

    wsed.projector = new THREE.Projector();
    wsed.onMouseDownPosition = new THREE.Vector2();
    wsed.ray = new THREE.Ray(wsed.camera.position, null);

    for (var ipmt = 0; ipmt < wsed.NPMTS; ipmt++) {
      var particle = new THREE.Particle(wsed.unhitMaterial);
      particle.position.x = pmtpos.x[ipmt]/50;
      particle.position.y = pmtpos.y[ipmt]/50;
      particle.position.z = pmtpos.z[ipmt]/50;
      wsed.scene.add(particle);
      wsed.pmts.push(particle);
    }

    wsed.renderer = new THREE.CanvasRenderer();
    wsed.renderer.setSize(window.innerWidth, window.innerHeight);

    wsed.container.appendChild( wsed.renderer.domElement );

    document.addEventListener('mousemove', wsed.events.onDocumentMouseMove, false);
    document.addEventListener('mousedown', wsed.events.onDocumentMouseDown, false);
    document.addEventListener('mouseup', wsed.events.onDocumentMouseUp, false);
    document.addEventListener('mousewheel', wsed.events.onDocumentMouseWheel, false);

    wsed.renderer.render(wsed.scene, wsed.camera);
  };

  wsed.update = function(data) {
    var nhits = data.t.length;

    var keep = new Array(wsed.prevHits.length);
    for (var icurr=0; icurr<nhits; icurr++) {
      for (var iprev=0; iprev<wsed.prevHits.length; iprev++) {
        if (data.id[icurr] == wsed.prevHits[iprev]) {
          keep[iprev] = true;
        }
      }
      var material = new THREE.ParticleCanvasMaterial({
        color: wsed.colors.jet(1.0*data.t[icurr]/4096, true),
        program: wsed.particleSurfaceProgram
      });
      wsed.pmts[data.id[icurr]].material = material;
      var ccc = getCCC(data.id[icurr]);
      var channel_selector = "#channel-" + ccc.crate + '_' + ccc.card + '_' + ccc.channel;
      $(channel_selector).css('background', wsed.colors.jet(1.0*data.t[icurr]/4096));
    }

    for (var ikeep=0; ikeep<keep.length; ikeep++) {
      if (!keep[ikeep]) {
        wsed.pmts[wsed.prevHits[ikeep]].material = wsed.unhitMaterial;
        var ccc = getCCC(wsed.prevHits[ikeep]);
        var channel_selector = "#channel-" + ccc.crate + '_' + ccc.card + '_' + ccc.channel;
        $(channel_selector).css('background','#333');
      }
    }
    wsed.render();
    delete keep;

    wsed.prevHits = data.id;

    // plots
    wsed.update_plot('charge', data.qhist);
    wsed.update_plot('time', data.thist);

    // metadata
    $("#meta-nhit").html('<strong>NHIT</strong>: ' + data.nhit);
    $("#meta-gtid").html('<strong>GTID</strong>: ' + data.gtid);
  };

  wsed.render = function() {
    wsed.renderer.render(wsed.scene, wsed.camera);
  };

  // events
  wsed.events = {
    onDocumentMouseDown: function(event) {
      event.preventDefault();
      wsed.isMouseDown = true;
      wsed.onMouseDownTheta = wsed.theta;
      wsed.onMouseDownPhi = wsed.phi;
      wsed.onMouseDownPosition.x = event.clientX;
      wsed.onMouseDownPosition.y = event.clientY;
    },

    onDocumentMouseMove: function(event) {
      event.preventDefault();

      if (wsed.isMouseDown) {
        wsed.theta = - ((event.clientX - wsed.onMouseDownPosition.x) * 0.5) + wsed.onMouseDownTheta;
        wsed.phi = ((event.clientY - wsed.onMouseDownPosition.y) * 0.5) + wsed.onMouseDownPhi;

        wsed.camera.position.x = wsed.radius * Math.sin(wsed.theta * Math.PI / 360) * Math.cos(wsed.phi * Math.PI / 360);
        wsed.camera.position.y = wsed.radius * Math.sin(wsed.phi * Math.PI / 360);
        wsed.camera.position.z = wsed.radius * Math.cos(wsed.theta * Math.PI / 360) * Math.cos(wsed.phi * Math.PI / 360);
        wsed.camera.updateMatrix();
        wsed.camera.lookAt(wsed.scene.position);
      }

      var mouseV = new THREE.Vector3((event.clientX / wsed.renderer.domElement.width) * 2 - 1, - (event.clientY / wsed.renderer.domElement.height) * 2 + 1, 0.5);
      wsed.mouse3D = wsed.projector.unprojectVector(mouseV, wsed.camera);
      wsed.ray.direction = wsed.mouse3D.subSelf(wsed.camera.position).normalize();

      wsed.render();

      delete mouseV;
    },

    onDocumentMouseUp: function(event) {
      event.preventDefault();
      wsed.isMouseDown = false;
      wsed.onMouseDownPosition.x = event.clientX - wsed.onMouseDownPosition.x;
      wsed.onMouseDownPosition.y = event.clientY - wsed.onMouseDownPosition.y;

      if (wsed.onMouseDownPosition.length() > 5)
        return;

      wsed.render();
    },

    onDocumentMouseWheel: function(event) {
      wsed.radius -= event.wheelDeltaY;

      wsed.camera.position.x = wsed.radius * Math.sin(wsed.theta * Math.PI / 360) * Math.cos(wsed.phi * Math.PI / 360);
      wsed.camera.position.y = wsed.radius * Math.sin(wsed.phi * Math.PI / 360);
      wsed.camera.position.z = wsed.radius * Math.cos(wsed.theta * Math.PI / 360) * Math.cos(wsed.phi * Math.PI / 360);
      wsed.camera.updateMatrix();

      wsed.render();
    }
  };

  // colors
  wsed.colors = {
    jet: function(val, hex) {
      function clamp(val, min, max) {
        return Math.max(min, Math.min(max, val));
      }

      var red   = Math.floor(clamp(255 * Math.min(4 * val - 1.5, -4 * val + 4.5), 0, 255));
      var green = Math.floor(clamp(255 * Math.min(4 * val - 0.5, -4 * val + 3.5), 0, 255));
      var blue  = Math.floor(clamp(255 * Math.min(4 * val + 0.5, -4 * val + 2.5), 0, 255));

      if (hex)
        return wsed.colors.rgb2hex(red, green, blue);

      return 'rgb(' + red + ',' + green + ',' + blue + ')'
    },

    rgb2hex: function(R,G,B) {
      function hexify(n) {
        n = parseInt(n,10);
        if (isNaN(n))
           return "00";
        n = Math.max(0,Math.min(n,255));
        return "0123456789ABCDEF".charAt((n-n%16)/16) + "0123456789ABCDEF".charAt(n%16);
      }

      var s = hexify(R) + hexify(G) + hexify(B);
      return '0x' + s;
    }
  };


  // plots
  wsed.plot_options = {
    series: { shadowSize: 0 }, // drawing is faster without shadows
    yaxis: { min: 0, max: 350 },
    xaxis: { min: 0, max: 4095 },
    bars: { show: true }
  };
  
  wsed.update_plot = function(name, data) {
    if (wsed.plots && wsed.plots[name]) {
      wsed.plots[name].setData([{label: name, data: data}]);
      wsed.plots[name].draw();
    }
  };

  return wsed;
}());

function getCCC(lcn) {
  return {
    'crate': (lcn >> 9) & ((1 << 5) - 1),
    'card': (lcn >> 5) & ((1 << 4) - 1),
    'channel': (lcn >> 0) & ((1 << 5) - 1)
  }
}

