from model import (
    apply_feedback,
    load_data,
    recommend_for_user,
    recommend_category_after_feedback,
    save_feedback,
)


def print_recommendations(results, cold_start, heading=None):
    if heading:
        print(f"\n{heading}")
    elif cold_start:
        print("\nNew customer: using popularity/ratings as fallback.")
    else:
        print("\nPersonalized recommendations:")

    for i, row in enumerate(results.itertuples(), 1):
        if cold_start:
            score_text = f"average={row.avg_rating:.2f}"
        else:
            score_text = f"prediction={row.predicted_score:.2f}/5"
        print(
            f"{i}. {row.service_name} | {row.category} | "
            f"${row.price:.2f} | {score_text}"
        )


def collect_feedback(user_id, results, cold_start):
    answer = input("\nWas this recommendation helpful? [Y/n]: ").strip().lower()
    if answer in {"", "y", "yes"}:
        save_feedback(user_id, helpful=True, reason="helpful")
        print("Thank you. Your feedback was recorded.")
        return

    if answer not in {"n", "no"}:
        print("Feedback skipped.")
        return

    print("\nWhat would improve the recommendation?")
    print("  1. Lower price")
    print("  2. Different category")
    print("  3. Show more alternatives")
    print("  4. Skip feedback")
    choice = input("Select an option [1-4]: ").strip()

    if choice == "1":
        save_feedback(user_id, helpful=False, reason="lower_price")
        adjusted = apply_feedback(results, reason="lower_price")
        print_recommendations(
            adjusted,
            cold_start,
            heading="Updated recommendations based on your feedback (lower price):",
        )
    elif choice == "2":
        services, _ = load_data()
        categories = sorted(services["category"].unique())
        print("Available categories: " + ", ".join(categories))
        new_category = input("Preferred category: ").strip()
        if not new_category:
            print("No category entered. Feedback skipped.")
            return
        save_feedback(
            user_id, helpful=False, reason="different_category", detail=new_category
        )
        adjusted, adjusted_cold_start = recommend_category_after_feedback(
            user_id=user_id,
            top_n=max(5, len(results)),
            category=new_category,
        )
        if adjusted.empty:
            print("No recommendations matched that category.")
        else:
            if adjusted_cold_start:
                print("Using historical ratings as fallback for this category.")
            print_recommendations(
                adjusted,
                adjusted_cold_start,
                heading=f"Updated recommendations for category '{new_category}':",
            )
    elif choice == "3":
        save_feedback(user_id, helpful=False, reason="more_alternatives")
        adjusted, adjusted_cold_start = recommend_for_user(
            user_id=user_id,
            top_n=min(max(len(results) + 3, 5), 20),
            category=None,
        )
        print_recommendations(
            adjusted,
            adjusted_cold_start,
            heading="Updated recommendations with more alternatives:",
        )
    else:
        print("Feedback skipped.")


def main():
    print("=" * 72)
    print("SERVICE RECOMMENDATION SYSTEM - TENSORFLOW")
    print("=" * 72)
    print("Existing customer examples: U001, U002, U003, ... U008")
    print("A new ID such as U100 demonstrates cold-start handling.\n")

    services, _ = load_data()
    categories = sorted(services["category"].unique())
    print("Available categories:")
    for category in categories:
        print(f"  - {category}")

    while True:
        user_id = input("\nCustomer ID (or 'exit'): ").strip()
        if user_id.lower() == "exit":
            print("Goodbye.")
            break
        if not user_id:
            continue

        category = input("Optional category [Enter = all]: ").strip() or None
        top_n_text = input("Number of recommendations [5]: ").strip()
        try:
            top_n = int(top_n_text) if top_n_text else 5
            top_n = max(1, min(top_n, 20))
        except ValueError:
            top_n = 5

        results, cold_start = recommend_for_user(
            user_id=user_id, top_n=top_n, category=category
        )

        if results.empty:
            print("\nNo recommendations matched the selected category.")
            continue

        print_recommendations(results, cold_start)
        collect_feedback(user_id, results, cold_start)


if __name__ == "__main__":
    main()
