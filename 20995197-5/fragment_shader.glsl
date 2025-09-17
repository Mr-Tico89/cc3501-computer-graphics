#version 330 core

in float v_angle;
in float v_density;

out vec4 fragColor;

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    if (v_density < 0.01) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    
    float hue = (v_angle + 3.14159) / (2.0 * 3.14159);
    float saturation = clamp(v_density, 0.0, 1.0);
    float value = mix(0.8, 1.0, clamp(v_density, 0.0, 1.0));
    
    vec3 hsv = vec3(hue, saturation, value);
    vec3 rgb = hsv2rgb(hsv);
    
    fragColor = vec4(rgb, 1.0);
}