using System.Reflection;
using PCTexturePackGeneratorConsole;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using CleanupUtils = TexturePackCleanup.Utils;

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

// Some higher res versions aren't used while LODs are (ie: croc_head vs croc_head_lod)
// so we save deletion for later to avoid looping over all files twice
//var filesToDelete = new List<(string, string)>();

// First loop to remove unused textures and rename LODs
foreach (var textureFileInfo in new DirectoryInfo(convertedTexturesFolder).GetFiles())
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
    //filesToDelete.Add((textureFileInfo.FullName, reasonToIgnore));
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
    File.Copy(Path.Join(convertedTexturesFolder, higherRes) + textureFileInfo.Extension, textureFileInfo.FullName, true);
    continue;
  }
}

//foreach (var (fileToDelete, reason) in filesToDelete)
//{
//  Console.WriteLine($"Removing {fileToDelete} because {reason}");
//  File.Delete(fileToDelete);
//}

Console.WriteLine($"\nConverting textures to Dolphin format...");
// First loop to do the Dolphin name and format conversion
foreach (var textureFileInfo in new DirectoryInfo(convertedTexturesFolder).GetFiles())
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
    var image = Image.Load(textureFileInfo.FullName);
    var (a, b) = SplitMethod((Image<Rgba32>)image);

    a.Save(Path.Join(destinationFolder, newNames[0]) + textureFileInfo.Extension);
    b.Save(Path.Join(destinationFolder, newNames[1]) + textureFileInfo.Extension);
    File.Delete(textureFileInfo.FullName);
  }
  else
  {
    File.Move(textureFileInfo.FullName, Path.Join(destinationFolder, newNames[0]) + textureFileInfo.Extension);
  }

}

return 0;
