using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using MrPumpkin.Web;
using MrPumpkin.Web.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// Register WebSocket service as singleton
builder.Services.AddSingleton<PumpkinWebSocketService>();

await builder.Build().RunAsync();
