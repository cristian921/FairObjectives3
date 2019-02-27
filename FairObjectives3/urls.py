"""FairObjectives3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from allocation import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view()),
    path('', views.index, name='index'),
    path('addAggregatedPortfolio/', views.add_aggregated_portfolio, name='aggregated_portfolio_form'),
    path('<int:pk>/deleteAggregatedPortfolio/', views.delete_aggregated_portfolio, name='delete_aggregated_portfolio'),
    path('<int:pk>/addAssetPortfolio/', views.add_asset_portfolio, name='add_asset_portfolio'),
    path('<int:pk>/deletePortfolioAsset/', views.delete_portfolio_asset, name='delete_portfolio_asset'),
    path('<int:pk>/updatePortfolioAsset/', views.update_asset_portfolio, name='delete_portfolio_asset'),
    path('addObjective/', views.add_objective, name="add_objective"),
    path('<int:pk>/updateObjective/', views.update_objective, name='update_objective'),
    path('<int:pk>/deleteObjective/', views.delete_objective, name='delete_objective'),
    path('addResources/', views.add_resources, name="add_resources"),
    path('<int:pk>/updateResources/', views.update_resources, name="update_resources"),
    path('<int:pk>/deleteResources/', views.delete_resources, name="delete_resources"),
    path('objectivesAllocation/', views.objectives_allocation_fun, name='objectives_allocation'),
    path('<int:pk>/deleteSolution/', views.delete_solution, name="delete_solution"),
    path('deleteAllSolution/', views.delete_all_solution, name="delete_all_solution"),
    path('viewObjectivesAllocation/', views.view_objective_allocation, name="chart"),
    path('bug/', views.founds_allocation_fun, name="chart"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
