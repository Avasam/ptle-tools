using System.Reflection;
using PCTexturePackGeneratorConsole;

(var pcArcFolder, var outputLocation) = Utils.ParseArguments(args);
var workingPath = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
var tempDirectory = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
var extractedTexturesFolder = $"{tempDirectory}/textures";
var convertedTexturesFolder = $"{tempDirectory}/textures_converted";
Directory.CreateDirectory(tempDirectory);

// PitfallARCTool.Program.Main(new string[]{ "-x", $"{pcArcFolder}/textures.arc", "-o", extractedTexturesFolder });
var exitCode = Utils.Execute($"{workingPath}\\PitfallARCTool.exe", $"-x \"{pcArcFolder}/textures.arc\" -o \"{extractedTexturesFolder}\" -e LE");
if (exitCode != 0) return exitCode;

// TexConvert.TexConvert.Main(new string[] { extractedTexturesFolder, convertedTexturesFolder });
exitCode = Utils.Execute($"{workingPath}\\TexConvert.exe", $"{extractedTexturesFolder} {convertedTexturesFolder}");
if (exitCode != 0) return exitCode;

foreach (var textureFileInfo in new DirectoryInfo(convertedTexturesFolder).GetFiles())
{
  var newName = Utils.TextureNameMapping.GetValueOrDefault(textureFileInfo.Name);
  //var newName = textureFileInfo.Name;
  if (string.IsNullOrEmpty(newName))
  {
    File.Delete(textureFileInfo.FullName);
  }
  else
  {
    var destinationFolder = $"{outputLocation}/GPHE52/";
    if (!File.Exists(destinationFolder))
    {
      Directory.CreateDirectory(destinationFolder);
    }
    File.Move(textureFileInfo.FullName, destinationFolder + newName);
  }
}

return 0;
