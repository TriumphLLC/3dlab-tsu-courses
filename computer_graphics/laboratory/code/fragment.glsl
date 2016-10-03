#version 150 compatibility

uniform sampler2D texSampler;

in vec2 tex_coord;

uniform vec2 resolution;
uniform vec2 direction;

vec4 blur5(sampler2D image, vec2 uv, vec2 resolution, vec2 direction) {
  vec4 color = vec4(0.0);
  vec2 off1 = vec2(1.3333333333333333) * direction;
  color += texture2D(image, uv) * 0.29411764705882354;
  color += texture2D(image, uv + (off1 / resolution)) * 0.35294117647058826;
  color += texture2D(image, uv - (off1 / resolution)) * 0.35294117647058826;
  return color;
}

void main()
{
    vec4 color = blur5(texSampler, tex_coord, resolution, direction);
    gl_FragColor = color;
}