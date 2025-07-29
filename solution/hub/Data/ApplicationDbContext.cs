using Microsoft.EntityFrameworkCore;
using hub.Models;
using FileModel = hub.Models.File;

namespace hub.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
        {
        }

        public DbSet<User> Users { get; set; }
        public DbSet<FileModel> Files { get; set; }
        public DbSet<Link> Links { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configuración específica para User
            modelBuilder.Entity<User>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.ToTable("users");
                
                entity.Property(e => e.Id)
                    .HasColumnName("id");
                
                entity.Property(e => e.FirstName)
                    .IsRequired()
                    .HasMaxLength(100)
                    .HasColumnName("first_name");
                
                entity.Property(e => e.LastName)
                    .IsRequired()
                    .HasMaxLength(100)
                    .HasColumnName("last_name");
                
                entity.Property(e => e.Email)
                    .IsRequired()
                    .HasMaxLength(255)
                    .HasColumnName("email");
                
                entity.Property(e => e.Password)
                    .IsRequired()
                    .HasColumnName("password");
                
                entity.Property(e => e.PhoneNumber)
                    .HasMaxLength(20)
                    .HasColumnName("phone_number");
                
                entity.Property(e => e.CreatedAt)
                    .HasDefaultValueSql("CURRENT_TIMESTAMP")
                    .HasColumnName("created_at");
                
                // Índice único para email
                entity.HasIndex(e => e.Email)
                    .IsUnique();
            });

            // Configuración específica para File
            modelBuilder.Entity<FileModel>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.ToTable("files");
                
                entity.Property(e => e.Id)
                    .HasColumnName("id");
                
                entity.Property(e => e.TotalLinks)
                    .IsRequired()
                    .HasColumnName("total_links");
                
                entity.Property(e => e.FilePath)
                    .IsRequired()
                    .HasMaxLength(500)
                    .HasColumnName("file_path");
                
                entity.Property(e => e.FileName)
                    .IsRequired()
                    .HasMaxLength(255)
                    .HasColumnName("file_name");
                
                entity.Property(e => e.TotalProcessed)
                    .IsRequired()
                    .HasColumnName("total_processed");
                
                entity.Property(e => e.TotalFailed)
                    .IsRequired()
                    .HasColumnName("total_failed");
                
                entity.Property(e => e.Status)
                    .IsRequired()
                    .HasMaxLength(50)
                    .HasColumnName("status");
                
                entity.Property(e => e.UploadedAt)
                    .HasDefaultValueSql("CURRENT_TIMESTAMP")
                    .HasColumnName("uploaded_at");
                
                entity.Property(e => e.UserId)
                    .IsRequired()
                    .HasColumnName("user_id");
                
                // Relación con User
                entity.HasOne(f => f.User)
                    .WithMany()
                    .HasForeignKey(f => f.UserId)
                    .OnDelete(DeleteBehavior.Cascade);
                
                // Índices
                entity.HasIndex(e => e.Status);
                entity.HasIndex(e => e.UploadedAt);
                entity.HasIndex(e => e.UserId);
            });

            // Configuración específica para Link
            modelBuilder.Entity<Link>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.ToTable("links");
                
                entity.Property(e => e.Id)
                    .HasColumnName("id");
                
                entity.Property(e => e.FileId)
                    .IsRequired()
                    .HasColumnName("file_id");
                
                entity.Property(e => e.Url)
                    .IsRequired()
                    .HasMaxLength(2000)
                    .HasColumnName("url");
                
                entity.Property(e => e.Title)
                    .HasMaxLength(500)
                    .HasColumnName("title");
                
                entity.Property(e => e.PostDate)
                    .HasColumnName("post_date");
                
                entity.Property(e => e.Content)
                    .HasColumnType("text")
                    .HasColumnName("content");
                
                entity.Property(e => e.PageExists)
                    .IsRequired()
                    .HasColumnName("page_exists");
                
                entity.Property(e => e.Success)
                    .IsRequired()
                    .HasColumnName("success");
                
                entity.Property(e => e.ErrorDescription)
                    .HasMaxLength(1000)
                    .HasColumnName("error_description");
                
                entity.Property(e => e.ProcessedDate)
                    .HasColumnName("processed_date");
                
                // Relación con File
                entity.HasOne(l => l.File)
                    .WithMany()
                    .HasForeignKey(l => l.FileId)
                    .OnDelete(DeleteBehavior.Cascade);
                
                // Índices
                entity.HasIndex(e => e.FileId);
                entity.HasIndex(e => e.Success);
                entity.HasIndex(e => e.ProcessedDate);
                entity.HasIndex(e => e.PageExists);
            });
        }
    }
}