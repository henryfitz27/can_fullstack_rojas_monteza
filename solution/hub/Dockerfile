# Use the official .NET 8 SDK image for building
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

# Set the working directory
WORKDIR /src

# Copy the project file and restore dependencies
COPY hub.csproj ./
RUN dotnet restore

# Copy the entire source code
COPY . .

# Build the application
RUN dotnet build "hub.csproj" -c Release -o /app/build

# Publish the application
FROM build AS publish
RUN dotnet publish "hub.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Use the official .NET 8 runtime image for the final stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final

# Set the working directory
WORKDIR /app

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Copy the published application from the build stage
COPY --from=publish /app/publish .

# Create directory for file uploads
RUN mkdir -p /app/files

# Expose the port that the application listens on
EXPOSE 5000

# Set environment variables
ENV ASPNETCORE_URLS=http://+:5000
ENV ASPNETCORE_ENVIRONMENT=Production

# Define the entry point
ENTRYPOINT ["dotnet", "hub.dll"]