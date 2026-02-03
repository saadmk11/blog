---
date: 2026-02-03
description: How to control NULL value placement when sorting Django QuerySets using F() expressions.
hide:
  - navigation
tags:
  - python
  - django
  - postgresql
title: Sorting Strategies for Optional Fields in Django
type: post
authors:
  - maksudul
---

# Sorting Strategies for Optional Fields in Django <br><small>February 03, 2026</small>

## Introduction

You're building an admin dashboard that displays users sorted by their most recent login. The goal is simple: identify your most engaged users to prioritize them for a new beta feature access.

You sort by `last_login` in descending order, expecting to see users who just logged in at the top. Instead, every user who has never logged in appears first, pushing your active users (the ones you actually care about) off the first page.

This happens because PostgreSQL (and several other databases) treats `NULL` as "larger than" any actual value when sorting in descending order. Users with no login history (`NULL`) sort before users who logged in seconds ago, which is the opposite of what you need.

<!-- more -->

Django's `F()` expressions with the `nulls_last` parameter give you precise control over this behavior.

!!! quote "PostgreSQL NULL Sorting Behavior"

    The `NULLS FIRST` and `NULLS LAST` options can be used to determine whether nulls appear before or after non-null values in the sort ordering. By default, null values sort as if larger than any non-null value; that is, `NULLS FIRST` is the default for `DESC` order, and `NULLS LAST` otherwise.

    \- [PostgreSQL Documentation: Sorting Rows (ORDER BY)](https://www.postgresql.org/docs/current/queries-order.html)

## The Modern Solution: `F` Expressions with `nulls_last`

Django's `F()` expressions let you tap directly into your database's sorting engine. You can use the `nulls_last` and `nulls_first` parameters to explicitly control where `NULL` values appear in your results and Django handles all the database-specific details for you.

Let's work with `User` model, which includes a `last_login` field:

```python
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    last_login = models.DateTimeField(null=True, blank=True)
    ...
```

### Descending Order (Most Recent First, Never-Logged-In Last)

To show the most recently active users first, with users who have never logged in at the bottom:

```python
from django.db.models import F
from accounts.models import User

# Sort by last login descending, keeping NULLs (never logged in) at the end
queryset = User.objects.order_by(F('last_login').desc(nulls_last=True))

# Resulting Order:
# 1. alice@example.com - Last login: 2 minutes ago
# 2. bob@example.com - Last login: 1 hour ago
# 3. charlie@example.com - Last login: 3 days ago
# 4. dave@example.com - Never logged in (NULL)
```

This generates SQL that looks something like (in PostgreSQL):

```sql
SELECT * FROM accounts_user ORDER BY last_login DESC NULLS LAST;
```

### Ascending Order (Oldest First, Never-Logged-In Last)

If you want to see who hasn't logged in for the longest time (perhaps to identify inactive accounts), but still keep never-logged-in users at the bottom:

```python
from django.db.models import F

# Sort by last login ascending, keeping NULLs at the end
queryset = User.objects.order_by(F('last_login').asc(nulls_last=True))

# Resulting Order:
# 1. charlie@example.com - Last login: 3 days ago
# 2. bob@example.com - Last login: 1 hour ago
# 3. alice@example.com - Last login: 2 minutes ago
# 4. dave@example.com - Never logged in (NULL)
```

### When You Want NULLs First

For some use cases like identifying users who need onboarding you might want never-logged-in users at the top:

```python
# Never logged in first, then descending by last login
queryset = User.objects.order_by(F('last_login').desc(nulls_first=True))

# Never logged in first, then ascending by last login
queryset = User.objects.order_by(F('last_login').asc(nulls_first=True))
```

The beauty of this approach is that it's efficient: you're delegating the work to the database engine rather than post-processing results in Python.

### Database Support and How Django Handles It

The `nulls_last` and `nulls_first` parameters work across all Django-supported databases, but how Django implements them depends on backend features:

**PostgreSQL and Oracle:** These databases support `NULLS FIRST/LAST` natively, so Django appends that modifier directly.

**MySQL, MariaDB, and SQLite:** These backends don’t support the `NULLS FIRST/LAST` modifier. Django emulates it by prepending a boolean sort key (`expression IS NULL` or `expression IS NOT NULL`) when the backend’s default null ordering doesn’t match the requested behavior for the chosen direction. If it already matches, Django leaves the SQL alone.

## Quick Refresher: How `order_by()` Works

Let's take a moment to recap Django's `order_by()` method and how it enables these powerful sorting options.

By default, QuerySets use whatever ordering is defined in your model's `Meta.ordering`. You can override this on a per-query basis:

```python
Entry.objects.filter(pub_date__year=2005).order_by("-pub_date", "headline")
```

The hyphen (`-`) means descending; no prefix means ascending. You can order by multiple fields, and Django will apply them left to right.

You can also order across relationships using the familiar double-underscore syntax:

```python
Entry.objects.order_by("blog__name", "headline")
```

Finally, you can order by expressions anything that evaluates to a value. This is where things get powerful:

```python
from django.db.models import Coalesce

Entry.objects.order_by(Coalesce("summary", "headline").desc())
```

This expression-based ordering is exactly what enables the `asc()` and `desc()` methods to accept `nulls_first` and `nulls_last` arguments.

## Understanding the Underlying Pattern: Boolean Sorting

While Django's `F().asc()` and `F().desc()` expressions with `nulls_last` and `nulls_first` are the recommended approach, you might encounter another pattern in older Django code or when working with raw SQL. Understanding this pattern is also useful because it’s the same technique Django may use internally when a backend doesn’t support `NULLS FIRST/LAST` and the requested null placement conflicts with the backend’s default.

The pattern relies on sorting by whether a field is null *before* sorting by the field value itself:

### The Key Insight

Django's `__isnull` lookup returns a boolean that databases can sort on. When treated as a sort key, `False` (has a value) comes before `True` (is NULL):

```python
queryset = User.objects.order_by(
    'last_login__isnull',  # False (has logged in) sorts before True (never logged in)
    '-last_login'          # Within the "has logged in" group, sort descending
)
```

This creates a two-level sort that groups records into "has data" and "no data" buckets.

### Variations

For ascending order:
```python
queryset = User.objects.order_by('last_login__isnull', 'last_login')
```

For NULLs first instead of last:
```python
queryset = User.objects.order_by('-last_login__isnull', 'last_login')
```

### Why This Works

Under the hood, databases treat boolean values as integers: `False` = 0, `True` = 1. Sorting by `last_login__isnull` means:
- Users who have logged in: 0
- Users who have never logged in: 1

Numerically, 0s sort before 1s, placing users with login history before users without.

**Note:** While this pattern works, using `F().desc(nulls_last=True)` is clearer and more maintainable for Django ORM queries.

## Conclusion

`NULL` values can create unexpected sort orders if you don't handle them deliberately. Django's `F().asc()` and `F().desc()` expressions with `nulls_last` and `nulls_first` give you precise control over where they appear on any database.

You write clear, explicit code (`F('last_login').desc(nulls_last=True)`) and Django handles all the database-specific details behind the scenes. Whether your database supports native `NULLS FIRST/LAST` syntax or not, your code stays the same.

Whether you're sorting by timestamps, optional prices, or any other nullable field, this feature ensures your data appears in a logical order for your users.

## References

* **Django Documentation:** [F() expressions](https://docs.djangoproject.com/en/stable/ref/models/expressions/#f-expressions)
* **Django Documentation:** [order_by() and QuerySet ordering](https://docs.djangoproject.com/en/stable/ref/models/querysets/#django.db.models.query.QuerySet.order_by)
* **PostgreSQL Documentation:** [Sorting Rows (ORDER BY)](https://www.postgresql.org/docs/current/queries-order.html)
* **Oracle Documentation:** [ORDER BY Clause](https://docs.oracle.com/javadb/10.10.1.2/ref/rrefsqlj13658.html)