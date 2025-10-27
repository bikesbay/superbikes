document.addEventListener("DOMContentLoaded", () => {
  const wishlistContainer = document.querySelector(".wishlist-container");

  // Function to show empty wishlist message
  function showEmptyMessage() {
    wishlistContainer.innerHTML = `
      <div class="empty-wishlist">
        <p>
          You have no bikes in your wishlist.<br />
          Click the ❤️ icon on a bike to add it here!
        </p>
      </div>
    `;
  }

  // Remove bike from wishlist
  wishlistContainer.addEventListener("click", async (e) => {
    if (!e.target.classList.contains("remove-bike")) return;

    const bikeId = e.target.dataset.id;
    const card = e.target.closest(".wishlist-card");

    if (!bikeId) {
      alert("Invalid bike ID");
      return;
    }

    try {
      const response = await fetch("/remove_from_wishlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bike_id: bikeId }),
      });
      const result = await response.json();

      if (result.status === "success") {
        card.style.transition = "opacity 0.4s ease";
        card.style.opacity = "0";
        setTimeout(() => {
          card.remove();
          if (
            wishlistContainer.querySelectorAll(".wishlist-card").length === 0
          ) {
            showEmptyMessage();
          }
        }, 400);
      } else {
        alert("❌ " + result.message);
      }
    } catch (err) {
      console.error(err);
      alert("An unexpected error occurred. Try again.");
    }
  });

  // Sidebar toggle logic
  const sidebarItems = document.querySelectorAll(".sidebar-menu li");
  const sections = {
    "wishlist-section": document.getElementById("wishlist-section"),
    "appointments-section": document.getElementById("appointments-section"),
  };

  sidebarItems.forEach((item) => {
    // Skip Logout link
    if (item.querySelector("a")) return;

    item.addEventListener("click", () => {
      // Remove active from all
      sidebarItems.forEach((i) => i.classList.remove("active"));
      // Set clicked item active
      item.classList.add("active");

      // Hide all sections
      Object.values(sections).forEach((sec) => (sec.style.display = "none"));

      // Show target section
      const target = item.getAttribute("data-target");
      if (sections[target]) sections[target].style.display = "block";
    });
  });
});
