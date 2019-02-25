// WadThePlanet planet viewer and editor component
// Based on Three.js (MIT-licensed) and JQuery

var renderer, scene;
var camera, cameraControls, raycaster;
var loadingManager, textureLoader, cubemapLoader;
var sunLight, skyCubemap;
var planetMesh;
var rmbDown = false; // Right mouse button pressed?

var textureCanvas; // JQuery selector to the <canvas> containing the painted texture
const TEXTURE_SIZE = 2048; // In pixels, must be power-of-two

var brush = {
    size: 50,
    colorpicker: null,
}

// === Setup code ==============================================================

function setup() {
    // Setups THREE.js; done once at startup

    // Setup renderer
    renderer = new THREE.WebGLRenderer({
        antialias: true,
        //alpha: true, // Enable transparent Canvas backround
    });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.gammaOutput = true; // Framebuffer output has premultiplied gamma
    //renderer.toneMappingExposure = 1.0;

    // Attach the Canvas to the main container, but hide it while loading
    renderer.domElement.id = 'editor';
    $('#editor-container').append(renderer.domElement);
    $('#editor').hide();

    // Setup scene and main camera
    scene = new THREE.Scene();

    // Setup texture loaders
    // FIXME(Paolo): Make this script into a template to use {% static 'path/to/textures' %}?
    loadingManager = new THREE.LoadingManager(onDoneLoading);

    textureLoader = new THREE.TextureLoader(loadingManager)
    textureLoader.setPath("/static/textures/");
    cubemapLoader = new THREE.CubeTextureLoader(loadingManager);
    cubemapLoader.setPath("/static/textures/skybox/");

    // Setup camera and camera controls
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0.0, 0.0, 3.0);
    scene.add(camera);

    cameraControls = new THREE.OrbitControls(camera, renderer.domElement);
    cameraControls.enablePan = false;
    cameraControls.rotateSpeed = 0.1;
    cameraControls.enableDamping = true;
    cameraControls.dampingFactor = 0.1;
    cameraControls.minDistance = 1.5;
    cameraControls.maxDistance = 100.0;

    // Create raycaster
    raycaster = new THREE.Raycaster();

    // Init entities
    setupEnvironment();
    setupPlanet();
    setupTextureCanvas();
    setupTools();

    // The editor will be shown automatically when all textures are loaded
    // (see `onDoneLoading()`)
}

function setupEnvironment() {
    // Adds lights and skybox to scene

    // Load starfield cubemap (order: [+X, -X, +Y, -Y, +Z, -Z])
    skyCubemap = cubemapLoader.load([
        "skybox_right1.png", "skybox_left2.png",
        "skybox_top3.png", "skybox_bottom4.png",
        "skybox_front5.png", "skybox_back6.png",
    ]);
    scene.background = skyCubemap;

    sunLight = new THREE.DirectionalLight(0xFFFFFE, 1.0);
    sunLight.position.set(10, 10, 10);
    sunLight.lookAt(0.0, 0.0, 0.0);
    scene.add(sunLight);
    // TODO(Paolo): Add sun mesh/billboard to scene

    //var ambientLight = new THREE.AmbientLight(0xFFFFFF, 0.0);
    //scene.add(ambientLight);
}

function setupPlanet() {
    // Generates the planet geometry and material[s]

    // Generate planet geometry. Use a normalized cube; this gives better UV
    // mapping than a SphereGeometry or IcosahedronGeometry!
    // TODO(Paolo): Add a slider for the user to control morphing between sphere and cube
    const radius = 1.0;
    const nSubdivs = 16;
    var geometry = new THREE.BoxGeometry(1.0, 1.0, 1.0, nSubdivs, nSubdivs, nSubdivs);
    for (let i = 0; i < geometry.vertices.length; i++) {
        var vtx = geometry.vertices[i];
        var distToCenter = radius + Math.random() * 0.06; // TODO(Paolo): Better heightmaps, fix random seed
        vtx.setLength(distToCenter);
    }

    geometry.computeVertexNormals();

    var material = new THREE.MeshStandardMaterial({
        //color: 0xFEFEFE,
        //map: textureLoader.load("planet/col.jpg"),
        normalMap: textureLoader.load("planet/nrm.jpg"),
        //aoMap: textureLoader.load("planet/AO.jpg"),
        roughnessMap: textureLoader.load("planet/rgh.jpg"),
        //displacementMap: textureLoader.load("planet/disp.jpg"),

        metalness: 0.0,
        //envMap: skyCubemap,
        //envMapIntensity: 1.0,
        shading: THREE.SmoothShading,
    });

    planetMesh = new THREE.Mesh(geometry, material);
    scene.add(planetMesh);
}

function setupTextureCanvas() {
    // Create and init `textureCanvas`, i.e. the Canvas that will hold the texture
    // painted by the user for the planet.

    var canvasCode = '<canvas width="' + TEXTURE_SIZE + '" height="' + TEXTURE_SIZE + '">'
    textureCanvas = $(canvasCode); // Create a new "free-floating" (out-of-DOM) <canvas>
    textureCanvas.width(TEXTURE_SIZE).height(TEXTURE_SIZE);
    textureCanvas.css('display', 'none'); // Hide it

    var ctx = textureCanvas[0].getContext("2d");
    ctx.fillStyle = "#20FA20";
    ctx.fillRect(0, 0, textureCanvas.width(), textureCanvas.height());

    var texture = new THREE.Texture(textureCanvas[0]);
    texture.anisotropy = 4;
    texture.needsUpdate = true;

    planetMesh.material.map = texture;
    planetMesh.material.map.needsUpdate = true;
}

function setupTools() {
    // Initializes the editor tools on the side toolbar.
    // Setup brush color picker
    brush.colorpicker = new Huebee('#colorpicker', {
        // options
        setBGColor: true,
        saturations: 3,
        shades: 10,
        notation: 'hex',
    });
}

function onDoneLoading() {
    // Run when the editor (and its textures) are done loading; hides the loading
    // spinner and shows the editor's <canvas>
    $('#editor-container #spinner').remove();
    $('#editor').fadeIn(500);
}

// === Event handlers and main code ============================================

function loop() {
    // Process input events and render; done once per frame
    cameraControls.update();

    renderer.render(scene, camera);
    requestAnimationFrame(loop); // Keep looping once per frame
}

function onWindowResize() {
    // Run when the broser window is resized
    var container = $('#editor-container');
    var width = container.innerWidth();
    var height = container.innerHeight();

    var oldAspect = camera.aspect;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    // Zoom out as the viewport gets more vertical
    // This way planets will get a somewhat correct scale on both vertical
    // screens (ex. mobile phones) and horizontal ones (ex. desktops)
    camera.position.multiplyScalar(oldAspect / camera.aspect);

    renderer.setSize(width, height);
}

function raycastPlanet(clientX, clientY) {
    // Returns the array of intersections obtained by raycasting to `planetMesh`
    // from the given client{X,Y} position onscreen.

    var editorBounds = $('#editor')[0].getBoundingClientRect();
    // Calculate mouse position relative to the editor, in UV coordinates (0.0 to 1.0)
    var mouseU = (clientX - editorBounds.left) / editorBounds.width;
    var mouseV = (clientY - editorBounds.top) / editorBounds.height;
    // Transform UV to normalized device coordinates (-1.0 to 1.0)
    var mouseNDC = new THREE.Vector2(mouseU * 2.0 - 1.0, -(mouseV * 2.0 - 1.0));

    // Raycast from the mouse position into the planet's geometry to find intersection points 
    raycaster.setFromCamera(mouseNDC, camera);
    return raycaster.intersectObject(planetMesh);
}

function paintPlanet(clientX, clientY, brushColor, brushSize, updateMap) {
    // Raycast to planet from `(clientX, clientY)`, then paint to
    // `textureCanvas` if there is any intersection.
    // If `updateMap`, set `planetMesh.material.map.needsUpdate` to tell THREE.js
    // that the texture has been updated (default true)

    var intersects = raycastPlanet(clientX, clientY);
    if (intersects.length > 0 && intersects[0].uv) {
        var uv = intersects[0].uv;
        planetMesh.material.map.transformUv(uv); // Transform the UV based on sampler params (repeat, flip...)

        var ctx = textureCanvas[0].getContext('2d');
        ctx.beginPath();
        ctx.arc(uv.x * textureCanvas.width(), uv.y * textureCanvas.height(),
            brushSize, 0.0, 2.0 * Math.PI);
        ctx.fillStyle = brush.colorpicker.color;
        ctx.fill();

        planetMesh.material.map.needsUpdate = updateMap || true;
    }
}

function onMouseDown(evt) {
    switch (evt.button) {
        case 0: // Left mouse button
            $('#editor-container').css('cursor', 'grab');
            break;

        case 2: // Right mouse button
            rmbDown = true;
            $('#editor-container').css('cursor', 'crosshair');
            paintPlanet(evt.clientX, evt.clientY, brush.color, brush.size);
            break;
    }
}

function onMouseUp(evt) {
    switch (evt.button) {
        case 2: // Right mouse button
            rmbDown = false;
            break;
    }

    $('#editor-container').css('cursor', 'default');
}

function onMouseMove(evt) {
    evt.preventDefault(); // (Stops the default mouse move event handlers)

    if (rmbDown) {
        paintPlanet(evt.clientX, evt.clientY, brush.color, brush.size);
    }
}

// === Attach event handlers ===================================================

$(document).ready(function () {
    setup();
    onWindowResize(); // Set canvas to correct size on startup by invoking `onWindowResize()`
    loop();
});
$(window).on('resize', onWindowResize);
$('#editor-container').on('mousedown', onMouseDown).on('mouseup', onMouseUp).on('mousemove', onMouseMove);