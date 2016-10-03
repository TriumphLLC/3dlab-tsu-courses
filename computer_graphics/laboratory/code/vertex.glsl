#version 150 compatibility

uniform float time;

in vec4 position;
in vec2 uv;

out vec2 tex_coord;

void main()
{
   tex_coord = uv;
   vec3 p = position.xyz;
   p.y += sin(time*p.y);
   p.x += cos(time*p.x);
   p.z += sin(time*p.z);
   gl_Position = gl_ModelViewProjectionMatrix * vec4(p, position.w);
}