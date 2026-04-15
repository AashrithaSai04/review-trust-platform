const { exec } = require('child_process');
exec('npm run build', (error, stdout, stderr) => {
  console.log("STDOUT:", stdout);
  console.log("STDERR:", stderr);
});
