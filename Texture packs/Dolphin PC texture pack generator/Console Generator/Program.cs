using System.Reflection;
using System.Text.Json;
using PCTexturePackGeneratorConsole;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;

(var pcArcFolder, var outputLocation) = Utils.ParseArguments(args);
var workingPath = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
var tempDirectory = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
var extractedTexturesFolder = $"{tempDirectory}\\textures";
var convertedTexturesFolder = $"{tempDirectory}\\textures_converted";
Directory.CreateDirectory(tempDirectory);

var exitCode = Utils.Execute(
  $"{workingPath}\\PitfallARCTool.exe",
  $"-x \"{pcArcFolder}\\textures.arc\" -o \"{extractedTexturesFolder}\" -e LE"
);
if (exitCode != 0) return exitCode;

exitCode = Utils.Execute(
  $"{workingPath}\\TexConvert.exe",
  $"--input {extractedTexturesFolder} --output {convertedTexturesFolder} --format png --vflip false"
);
Console.WriteLine("");
if (exitCode != 0) return exitCode;

var destinationFolder = $"{outputLocation}\\GPHE52\\";
if (!File.Exists(destinationFolder))
{
  Directory.CreateDirectory(destinationFolder);
}

foreach (var textureFileInfo in new DirectoryInfo(convertedTexturesFolder).GetFiles())
{
  var dteTextureMapJson = File.ReadAllText(".\\DTETextureMap.jsonc");
  var dteTextureMap = JsonSerializer.Deserialize<Dictionary<string, List<string>>>(
    dteTextureMapJson,
    new JsonSerializerOptions { ReadCommentHandling = JsonCommentHandling.Skip }
  );
  if (dteTextureMap == null) throw new NullReferenceException(nameof(dteTextureMap) + " is null.");

  var textureFileName = textureFileInfo.Name[..^textureFileInfo.Extension.Length];
  var newNames = dteTextureMap.GetValueOrDefault(textureFileName) ?? new List<string>();

  if (newNames.Count > 2) throw new ArgumentException("Split textures should be at most 2 elements", nameof(newNames));

  var reasonToIgnore = "";
  if (textureFileName == "font_pitfall_harry_s24_p0")
  {
    // FIXME: This COULD be fixed with a lot of hardcoded image manipulation
    // NOTE: Wii fonts are actually higher quality than PC! So we don't want them there either
    reasonToIgnore = "fonts are not aligned the same on PC";
  }
  else if (Utils.LodMapping.ContainsKey(textureFileName))
  {
    // Ignore lower resolution versions of textures
    reasonToIgnore = "there's a higher resolution texture available";
  }
  else if (newNames.Count <= 0)
  {
    // PC has some extra files
    reasonToIgnore = "it does not exist in the GameCube version's textures archive";
  }
  else if (Utils.UnusedTextures.Contains(textureFileName))
  {
    // Reduce the Texture Pack size
    reasonToIgnore = "it's known to be unused on GameCube & Wii";
  }
  if (reasonToIgnore != "")
  {
    Console.WriteLine($"Skipping {textureFileName} because {reasonToIgnore}");
    File.Delete(textureFileInfo.FullName);
    continue;
  }

  if (newNames.Count == 2)
  {
    var imageFormat = newNames[0][^2..];

    Func<Image<Rgba32>, (Image<Rgba32>, Image<Rgba32>)> SplitMethod = imageFormat switch
    {
      "_8" or "_9" => ImageUtils.SplitBATexture,
      "14" => ImageUtils.SplitAlphaTexture,
      _ => throw new ArgumentOutOfRangeException(nameof(imageFormat), $"Unknown GX format {imageFormat}"),
    };
    var image = Image.Load(textureFileInfo.FullName);
    var (a, b) = SplitMethod((Image<Rgba32>)image);

    a.Save(destinationFolder + newNames[0] + textureFileInfo.Extension);
    b.Save(destinationFolder + newNames[1] + textureFileInfo.Extension);
    File.Delete(textureFileInfo.FullName);
  }
  else
  {
    File.Move(textureFileInfo.FullName, destinationFolder + newNames[0] + textureFileInfo.Extension);
  }

}

return 0;
