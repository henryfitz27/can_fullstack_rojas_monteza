using hub.Data;
using hub.Services;
using hub.Interfaces;
using hub.Repositories;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// Configurar Entity Framework con PostgreSQL
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// Registrar repositorios
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IFileRepository, FileRepository>();

// Registrar servicio JWT
builder.Services.AddScoped<IJwtService, JwtService>();

// Configurar autenticación JWT
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.ASCII.GetBytes(
                builder.Configuration["Jwt:SecretKey"] ?? throw new InvalidOperationException("JWT SecretKey no configurado"))),
            ValidateIssuer = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidateAudience = true,
            ValidAudience = builder.Configuration["Jwt:Audience"],
            ValidateLifetime = true,
            ClockSkew = TimeSpan.Zero
        };
    });

builder.Services.AddAuthorization();

builder.Services.AddControllers();
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Aplicar migraciones automáticamente
await ApplyMigrationsAsync(app);

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();

static async Task ApplyMigrationsAsync(WebApplication app)
{
    using var scope = app.Services.CreateScope();
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    var logger = scope.ServiceProvider.GetRequiredService<ILogger<Program>>();
    var configuration = scope.ServiceProvider.GetRequiredService<IConfiguration>();

    // Leer configuración de base de datos
    var autoMigrate = configuration.GetValue<bool>("Database:AutoMigrate", app.Environment.IsDevelopment());
    var ensureCreated = configuration.GetValue<bool>("Database:EnsureCreated", app.Environment.IsDevelopment());

    if (!autoMigrate && !ensureCreated)
    {
        logger.LogInformation("Las migraciones automáticas están deshabilitadas.");
        return;
    }

    try
    {
        logger.LogInformation("Iniciando aplicación de migraciones...");

        // Verificar si la base de datos puede conectarse
        var canConnect = await context.Database.CanConnectAsync();
        if (!canConnect && ensureCreated)
        {
            logger.LogWarning("No se puede conectar a la base de datos. Intentando crear...");
            await context.Database.EnsureCreatedAsync();
        }

        if (autoMigrate)
        {
            // Verificar si hay migraciones pendientes
            var pendingMigrations = await context.Database.GetPendingMigrationsAsync();
            if (pendingMigrations.Any())
            {
                logger.LogInformation("Aplicando {Count} migraciones pendientes: {Migrations}",
                    pendingMigrations.Count(), string.Join(", ", pendingMigrations));

                await context.Database.MigrateAsync();
                logger.LogInformation("Migraciones aplicadas exitosamente.");
            }
            else
            {
                logger.LogInformation("No hay migraciones pendientes.");
            }
        }
    }
    catch (Exception ex)
    {
        logger.LogError(ex, "Error al aplicar migraciones: {Message}", ex.Message);

        // En desarrollo, puedes decidir si quieres que falle la aplicación
        if (app.Environment.IsDevelopment())
        {
            throw; // Re-lanza la excepción para detener la aplicación
        }

        // En producción, registra el error pero permite que la aplicación continúe
        logger.LogWarning("La aplicación continuará sin aplicar migraciones.");
    }
}

