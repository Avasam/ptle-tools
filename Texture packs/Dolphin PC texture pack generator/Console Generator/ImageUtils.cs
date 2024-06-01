using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;

namespace PCTexturePackGeneratorConsole;

internal class ImageUtils
{
  // Copied from TexConvert.cs
  public static (Image<Rgba32>, Image<Rgba32>) SplitAlphaTexture(Image<Rgba32> image)
  {
    var colorPixels = new Rgba32[image.Width * image.Height];
    var alphaPixels = new Rgba32[image.Width * image.Height];
    image.CopyPixelDataTo(colorPixels);
    image.CopyPixelDataTo(alphaPixels);
    for (var i = 0; i < colorPixels.Length; i++)
    {
      colorPixels[i].A = 255;
      alphaPixels[i] = new Rgba32(0, alphaPixels[i].A, 0, 255);
    }

    return (
        Image.LoadPixelData(colorPixels, image.Width, image.Height),
        Image.LoadPixelData(alphaPixels, image.Width, image.Height));
  }

  // Copied from TexConvert.cs
  public static (Image<Rgba32>, Image<Rgba32>) SplitBATexture(Image<Rgba32> image)
  {
    var rgPixels = new Rgba32[image.Width * image.Height];
    var baPixels = new Rgba32[image.Width * image.Height];
    image.CopyPixelDataTo(rgPixels);
    image.CopyPixelDataTo(baPixels);
    for (var i = 0; i < rgPixels.Length; i++)
    {
      rgPixels[i] = new Rgba32(rgPixels[i].R, rgPixels[i].R, rgPixels[i].R, rgPixels[i].G);
      baPixels[i] = new Rgba32(baPixels[i].B, baPixels[i].B, baPixels[i].B, baPixels[i].A);
    }

    return (
        Image.LoadPixelData(rgPixels, image.Width, image.Height),
        Image.LoadPixelData(baPixels, image.Width, image.Height));
  }
}
