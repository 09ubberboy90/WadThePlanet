// WadThePlanet planet viewer and editor component
// Based on Three.js (MIT-licensed) and JQuery

var renderer, scene;
var camera, cameraControls;
var textureLoader, cubemapLoader;
var sunLight, skyCubemap;
var planetMesh;

function setup() {
    // Setups THREE.js; done once at startup

    // Setup renderer
    renderer = new THREE.WebGLRenderer({
        antialias: true,
        //alpha: true, // Enable transparent Canvas backround
    });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.gammaInput = true; // Input textures have premultiplied gamma
    renderer.gammaOutput = true; // Framebuffer output has premultiplied gamma
    //renderer.toneMappingExposure = 5.0;

    // Attach the Canvas to the main container
    $('#editor-container').append(renderer.domElement);  

    // Setup scene and main camera
    scene = new THREE.Scene();

    // Setup texture loaders
    // FIXME(Paolo): Make this script into a template to use {% static 'path/to/textures' %}?
    textureLoader = new THREE.TextureLoader();
    textureLoader.setPath("/static/textures/");
    cubemapLoader = new THREE.CubeTextureLoader();
    cubemapLoader.setPath("/static/textures/skybox/");

    // Setup camera and camera controls
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0.0, 0.0, 1.0);
    scene.add(camera);

    cameraControls = new THREE.OrbitControls(camera, renderer.domElement);
    cameraControls.enablePan = false;
    cameraControls.enableDamping = true;
    cameraControls.dampingFactor = 0.1;
    cameraControls.screenSpacePanning = false;
    cameraControls.rotateSpeed = 0.1;
    cameraControls.minDistance = 1.5;
    cameraControls.maxDistance = 100.0;

    // Init 3D entities
    setupEnvironment();
    setupPlanet();
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

    //var ambientLight = new THREE.AmbientLight(0xFFFFFF, 0.3);
    //scene.add(ambientLight);
    sunLight = new THREE.DirectionalLight(0xFFFFFE, 1.0);
    sunLight.position.set(10, 10, 10);
    sunLight.lookAt(0.0, 0.0, 0.0);
    scene.add(sunLight);

    // TODO(Paolo): Add sun mesh/billboard to scene
}

function setupPlanet() {
    // Generates the planet geometry and material[s]

    // Generate planet geometry. Use a normalized cube; this gives better UV
    // mapping than a SphereGeometry or IcosahedronGeometry!
    const radius = 1.0;
    const nSubdivs = 16;
    var geometry = new THREE.BoxGeometry(1.0, 1.0, 1.0, nSubdivs, nSubdivs, nSubdivs);
    for(let i = 0; i < geometry.vertices.length; i ++) {
        var vtx = geometry.vertices[i];
        var distToCenter = radius + Math.random() * 0.06;  // TODO(Paolo): Better heightmaps, fix random seed
        vtx.setLength(distToCenter);
    }
    geometry.computeVertexNormals();

    var material = new THREE.MeshStandardMaterial({
        //color: 0xFEFEFE,
        map: textureLoader.load("planet/col.jpg"),
        normalMap: textureLoader.load("planet/nrm.jpg"),
        aoMap: textureLoader.load("planet/AO.jpg"),
        roughnessMap: textureLoader.load("planet/rgh.jpg"),
        //displacementMap: textureLoader.load("planet/disp.jpg"),

        metalness: 0.1,
        envMap: skyCubemap,
        //envMapIntensity: 1.0,
        shading: THREE.SmoothShading,
    });

    planetMesh = new THREE.Mesh(geometry, material);
    scene.add(planetMesh);
}

function loop() {
    // Process input events and render; done once per frame
    cameraControls.update();

    renderer.render(scene, camera);
    requestAnimationFrame(loop); // Keep looping once per frame
}

function onWindowResized() {
    // Run when the broser window is resized
    var container = $('#editor-container');
    var width = container.innerWidth(), height = container.innerHeight();

    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
}

$(document).ready(function() {
    setup();
    onWindowResized(); // Set canvas to correct size on startup
    loop();
});

$(window).resize(onWindowResized);