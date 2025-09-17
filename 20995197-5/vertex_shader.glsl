#version 330 core

in vec2 position;
in float angle;
in float density;

out float v_angle;
out float v_density;

void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    gl_PointSize = 3.0;
    v_angle = angle;
    v_density = density;
}