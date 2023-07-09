using System.IO.Compression;
using System.Reflection;
using System.Text.Json;
using PCTexturePackGeneratorConsole;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;
using CleanupUtils = TexturePackCleanup.Utils;

const string PACK_NAME = "PTLE-PC-resource-pack";
(var pcArcFolder, var outputLocation) = Utils.ParseArguments(args);
var workingPath = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
var tempDirectory = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
var extractedTexturesFolder = $"{tempDirectory}\\textures";
var convertedTexturesDirectoryInfo = new DirectoryInfo($"{tempDirectory}\\textures_converted");
var workingPackFolder = Path.Join(convertedTexturesDirectoryInfo.FullName, PACK_NAME);
var gcGameTexturesFolder = Path.Join(workingPackFolder, "textures", "GPH");
var wiiGameTexturesFolder = Path.Join(workingPackFolder, "textures", "RPF");

Directory.CreateDirectory(tempDirectory);

var exitCode = Utils.Execute(
  $"{workingPath}\\PitfallARCTool.exe",
  $"-x \"{pcArcFolder}\\textures.arc\" -o \"{extractedTexturesFolder}\" -e LE"
);
if (exitCode != 0) return exitCode;

exitCode = Utils.Execute(
  $"{workingPath}\\TexConvert.exe",
  $"--input {extractedTexturesFolder} --output {convertedTexturesDirectoryInfo} --format png --vflip false"
);
Console.WriteLine("");
if (exitCode != 0) return exitCode;


Directory.CreateDirectory(workingPackFolder);
Directory.CreateDirectory(gcGameTexturesFolder);
Directory.CreateDirectory(wiiGameTexturesFolder);
Console.WriteLine("Copying tikishield.png as logo.png");
using (var logo = Image.Load(Path.Join(convertedTexturesDirectoryInfo.FullName, "tikishield.png")))
using (var copy = logo.Clone(clone => clone.Flip(FlipMode.Vertical)))
{
  copy.Save(Path.Join(workingPackFolder, "logo.png"));
}
Console.WriteLine("Creating manifest.json");
File.WriteAllText(
  Path.Join(workingPackFolder, "manifest.json"),
  JsonSerializer.Serialize(new Utils.Manifest()
  {
    name = PACK_NAME.Replace("-", " "),
    id = PACK_NAME,
    version = "1",
    description = "An auto-generated pack using the PC version's textures. LODs also have been replaced by their higher resolution textures.",
    authors = new[] { "Avasam", "UltiNaruto", "Helco" },
    website = "https://github.com/Avasam/ptle-tools/tree/main/Texture%20packs/Dolphin%20PC%20texture%20pack%20generator",
    compressed = true,
  })
);
Console.WriteLine("");


// First loop to remove unused textures and rename LODs
foreach (var textureFileInfo in convertedTexturesDirectoryInfo.GetFiles())
{
  var textureFileName = textureFileInfo.Name[..^textureFileInfo.Extension.Length];

  var reasonToIgnore = "";
  if (textureFileName == "font_pitfall_harry_s24_p0")
  {
    // FIXME: This COULD be fixed with a lot of hardcoded image manipulation
    // NOTE: Wii fonts are actually higher quality than PC! So we don't want them there either
    reasonToIgnore = "fonts are not aligned the same on PC";
  }
  else
  {
    CleanupUtils.IsUsedOnDolphin(textureFileName, false, out reasonToIgnore);
  }

  if (reasonToIgnore != "")
  {
    Console.WriteLine($"Removing {textureFileName} because {reasonToIgnore}");
    File.Delete(textureFileInfo.FullName);
    continue;
  }

  var higherRes = CleanupUtils.LodMapping.GetValueOrDefault(textureFileName);
  if (higherRes != null)
  {
    // Ignore lower resolution versions of textures
    Console.WriteLine($"Replacing LOD {textureFileName} with higher resolution {higherRes}");
    // Assume same file extension
    File.Copy(Path.Join(convertedTexturesDirectoryInfo.FullName, higherRes) + textureFileInfo.Extension, textureFileInfo.FullName, true);
    continue;
  }
}


Console.WriteLine("\nConverting textures to Dolphin format...");
// Second loop to do the Dolphin name and format conversion
foreach (var textureFileInfo in convertedTexturesDirectoryInfo.GetFiles())
{
  var textureFileName = textureFileInfo.Name[..^textureFileInfo.Extension.Length];

  var newNames = CleanupUtils.DteTextureMap.GetValueOrDefault(textureFileName) ?? Array.Empty<string>();
  if (newNames.Length > 2) throw new ArgumentException("Split textures should be at most 2 elements", nameof(newNames));
  if (newNames.Length == 2)
  {
    var imageFormat = newNames[0][^2..];

    Func<Image<Rgba32>, (Image<Rgba32>, Image<Rgba32>)> SplitMethod = imageFormat switch
    {
      "_8" or "_9" => ImageUtils.SplitBATexture,
      "14" => ImageUtils.SplitAlphaTexture,
      _ => throw new ArgumentOutOfRangeException(nameof(imageFormat), $"Unknown GX format {imageFormat}"),
    };
    using (var image = Image.Load(textureFileInfo.FullName))
    {
      var (a, b) = SplitMethod((Image<Rgba32>)image);

      a.Save(Path.Join(gcGameTexturesFolder, newNames[0]) + textureFileInfo.Extension);
      a.Save(Path.Join(wiiGameTexturesFolder, newNames[0]) + textureFileInfo.Extension);
      b.Save(Path.Join(gcGameTexturesFolder, newNames[1]) + textureFileInfo.Extension);
      b.Save(Path.Join(wiiGameTexturesFolder, newNames[1]) + textureFileInfo.Extension);
      a.Dispose();
      b.Dispose();
    }
    File.Delete(textureFileInfo.FullName);
  }
  else
  {
    File.Copy(textureFileInfo.FullName, Path.Join(gcGameTexturesFolder, newNames[0]) + textureFileInfo.Extension);
    File.Move(textureFileInfo.FullName, Path.Join(wiiGameTexturesFolder, newNames[0]) + textureFileInfo.Extension);
  }
}

var resorucePackFilePath = Path.Join(outputLocation, PACK_NAME) + ".zip";
Console.WriteLine($"Compressing and copying pack to {resorucePackFilePath}");
if (File.Exists(resorucePackFilePath))
{
  File.Delete(resorucePackFilePath);
}
ZipFile.CreateFromDirectory(workingPackFolder, resorucePackFilePath, CompressionLevel.SmallestSize, false);

Console.WriteLine("Done!");
return 0;
