#version 330 core

uniform sampler2D densityTexture;
uniform sampler2D angleTexture;
uniform vec2 resolution;
uniform float maxDensity;

in vec2 fragCoord;
out vec4 fragColor;

// Función para convertir HSV a RGB
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec2 uv = (fragCoord + 1.0) * 0.5; // Convertir de [-1,1] a [0,1]
    
    float density = texture(densityTexture, uv).r;
    float angle = texture(angleTexture, uv).r;
    
    if (density < 0.001) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0); // Fondo negro
        return;
    }
    
    // Normalizar densidad
    float normalizedDensity = clamp(density / maxDensity, 0.0, 1.0);
    
    // Mapeo HSV
    float hue = angle / (2.0 * 3.14159265); // Normalizar ángulo a [0,1]
    if (hue < 0.0) hue += 1.0; // Asegurar que esté en [0,1]
    
    float saturation = normalizedDensity; // Mayor densidad = mayor saturación
    float value = mix(0.8, 1.0, normalizedDensity); // Brillo alto para áreas visitadas
    
    vec3 hsv = vec3(hue, saturation, value);
    vec3 rgb = hsv2rgb(hsv);
    
    fragColor = vec4(rgb, 1.0);
}
